"""
app.payments

Unified payment layer.

Providers
- Stripe: international payments via Stripe Checkout Sessions.
- Asaas: Brazil PIX via Asaas.

Public API
- create_payment_for_user(...)

The bot runs Telegram polling. To auto-activate VIP after payment, the bot also
runs an embedded aiohttp web server (see app.main) for webhooks.
"""

from __future__ import annotations

import base64
import logging
import os
import json
import hashlib
import hmac
from datetime import datetime, timedelta
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class PaymentCreateResult:
    provider: str
    external_id: str
    amount: float
    currency: str
    checkout_url: Optional[str] = None
    # PIX extras (Brazil)
    pix_qr_code: Optional[str] = None
    pix_qr_code_png_bytes: Optional[bytes] = None
    # Crypto extras (NOWPayments)
    crypto_pay_address: Optional[str] = None
    crypto_pay_amount: Optional[float] = None
    crypto_pay_currency: Optional[str] = None
    raw_provider_payload: Optional[Dict[str, Any]] = None


class StripeClient:
    """
    Minimal Stripe wrapper using Checkout Sessions.
    """
    def __init__(self) -> None:
        self.secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.success_url = os.getenv("STRIPE_SUCCESS_URL")  # optional
        self.cancel_url = os.getenv("STRIPE_CANCEL_URL")    # optional

        if not self.secret_key:
            raise ValueError("STRIPE_SECRET_KEY is not set")

        try:
            import stripe  # type: ignore
        except Exception as e:
            raise ImportError("Missing dependency 'stripe'. Add it to requirements.txt") from e

        stripe.api_key = self.secret_key
        self._stripe = stripe

    def create_checkout_session(
        self,
        *,
        user_id: int,
        plan: str,
        amount: float,
        currency: str,
        base_url: str,
        lang: str,
    ) -> PaymentCreateResult:
        """
        Creates a one-time Checkout Session.

        We rely on `checkout.session.completed` webhook events to activate the license.
        """
        stripe = self._stripe

        success_url = self.success_url or (base_url.rstrip("/") + "/stripe/success")
        cancel_url = self.cancel_url or (base_url.rstrip("/") + "/stripe/cancel")

        # Stripe expects integer minor units (cents). For zero-decimal currencies, this differs.
        # Here we keep USD (2 decimals) for this bot's default plans.
        unit_amount = int(round(amount * 100))

        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": currency.lower(),
                        "product_data": {"name": f"VIP {plan}"},
                        "unit_amount": unit_amount,
                    },
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(user_id),
                "plan": plan,
                "lang": lang,
            },
        )

        return PaymentCreateResult(
            provider="stripe",
            external_id=session["id"],
            amount=amount,
            currency=currency,
            checkout_url=session.get("url"),
        )


def is_stripe_no_payment_methods_error(exc: Exception) -> bool:
    """Detect Stripe error for unavailable payment methods.

    IMPORTANT: We only special-case this exact class of errors (as requested),
    because it commonly happens when the Stripe account is still under review
    or has not enabled card payment methods yet.
    """
    msg = str(exc) if exc else ""
    return ("No valid payment method types" in msg) or ("payment methods compatible" in msg)


def stripe_available() -> bool:
    return bool(os.getenv("STRIPE_SECRET_KEY"))


def get_asaas_pix_link(plan: str) -> str:
    """Return the Asaas PIX payment link for a given plan.

    Expected env vars:
      - ASAAS_PIX_LINK_WEEKLY
      - ASAAS_PIX_LINK_MONTHLY
      - ASAAS_PIX_LINK_LIFETIME

    Returns empty string if not configured.
    """
    key = {
        "weekly": "ASAAS_PIX_LINK_WEEKLY",
        "monthly": "ASAAS_PIX_LINK_MONTHLY",
        "lifetime": "ASAAS_PIX_LINK_LIFETIME",
    }.get(plan, "")
    if not key:
        return ""
    return (os.getenv(key) or "").strip()


def asaas_available() -> bool:
    # For the A2 flow (payment link + manual confirmation), we need:
    #  - an API token to verify the payment id
    #  - at least one payment link configured
    if not os.getenv("ASAAS_ACCESS_TOKEN"):
        return False
    return any(
        bool((os.getenv(k) or "").strip())
        for k in ("ASAAS_PIX_LINK_WEEKLY", "ASAAS_PIX_LINK_MONTHLY", "ASAAS_PIX_LINK_LIFETIME")
    )



def nowpayments_disabled_plans() -> set[str]:
    """Return set of plan keys for which NOWPayments should be hidden/disabled.

    Configure via env NOWPAYMENTS_DISABLED_PLANS as a comma-separated list, e.g.:
      NOWPAYMENTS_DISABLED_PLANS=weekly,weekly_ds
    """
    raw = os.getenv("NOWPAYMENTS_DISABLED_PLANS", "").strip()
    if not raw:
        return set()
    return {p.strip().lower() for p in raw.split(",") if p.strip()}


def nowpayments_allowed_for_plan(plan: str) -> bool:
    """Return True if NOWPayments should be offered for this plan."""
    plan_key = (plan or "").strip().lower()
    return plan_key not in nowpayments_disabled_plans()

def nowpayments_available() -> bool:
    """Return True if NOWPayments is configured enough to OFFER it as a payment option.

    We only require NOWPAYMENTS_API_KEY to create payments. NOWPAYMENTS_IPN_SECRET is
    strongly recommended for webhook signature validation; if it is missing, payments
    can still be confirmed via the manual "check payment" flow.
    """
    return bool(os.getenv("NOWPAYMENTS_API_KEY"))


def create_payment_explicit(
    *,
    provider: str,
    user_id: int,
    plan: str,
    lang: str,
    amount: float,
    currency: str,
    base_url: str,
) -> PaymentCreateResult:
    """Create a payment using an explicitly chosen provider.

    This function exists so the user can SELECT the payment method.
    It does NOT auto-fallback between gateways (except via UI logic).
    """
    provider = (provider or "").lower().strip()
    if provider == "stripe":
        client = StripeClient()
        return client.create_checkout_session(
            user_id=user_id,
            plan=plan,
            amount=amount,
            currency=currency,
            base_url=base_url,
            lang=lang,
        )

    if provider in ("asaas", "pix"):
        # A2 flow: we do NOT create a PIX charge via API (which requires CPF/CNPJ).
        # Instead, we send the user to an Asaas Payment Link and later ask them to
        # paste the Asaas payment id for verification.
        link = get_asaas_pix_link(plan)
        if not link:
            raise RuntimeError("Asaas PIX link is not configured for this plan")
        external_id = f"asaaslink:{user_id}:{plan}:{int(time.time())}"
        return PaymentCreateResult(
            provider="asaas",
            external_id=external_id,
            amount=float(amount),
            currency=str(currency).upper(),
            checkout_url=link,
            raw_provider_payload={"link": link, "mode": "payment_link"},
        )

    if provider in ("nowpayments", "crypto"):
        np = NowPaymentsClient()
        payment = np.create_payment(
            user_id=user_id,
            plan=plan,
            amount=amount,
            currency=currency,
            base_url=base_url,
            order_description=f"VIP {plan}",
        )
        # Enrich best-effort
        try:
            raw = np.get_payment(payment.external_id)
        except Exception:
            raw = None
        if isinstance(raw, dict):
            payment.crypto_pay_address = raw.get("pay_address") or raw.get("payaddress")
            try:
                payment.crypto_pay_amount = float(raw.get("pay_amount") or raw.get("payamount") or 0) or None
            except Exception:
                payment.crypto_pay_amount = None
            payment.crypto_pay_currency = raw.get("pay_currency") or raw.get("paycurrency")
            payment.raw_provider_payload = raw
        return payment

    raise ValueError(f"Unknown payment provider: {provider}")


class AsaasClient:
    """Minimal Asaas wrapper for PIX charges (Brazil).

    Authentication: send API key in header `access_token`.
    Main flow:
      1) ensure a customer exists (we store `asaas_customer_id` in users table)
      2) create a payment with billingType=PIX
      3) fetch Pix QR code payload + image via /v3/payments/{id}/pixQrCode
    """

    def __init__(self) -> None:
        self.access_token = os.getenv("ASAAS_ACCESS_TOKEN")
        self.base_url = os.getenv("ASAAS_BASE_URL", "https://api.asaas.com").rstrip("/")
        # Optional: webhook token to validate inbound webhook requests
        self.webhook_token = os.getenv("ASAAS_WEBHOOK_TOKEN") or None

        if not self.access_token:
            raise ValueError("ASAAS_ACCESS_TOKEN is not set")

        self._session = requests.Session()
        self._session.headers.update({
            "access_token": self.access_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "viponlybot/1.0",
        })

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = self._session.post(url, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"Asaas API error {r.status_code}: {r.text[:300]}")
        return r.json()

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = self._session.get(url, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"Asaas API error {r.status_code}: {r.text[:300]}")
        return r.json()

    def create_customer(self, *, user_id: int, name: str, email: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {"name": name}
        if email:
            payload["email"] = email
        data = self._post("/v3/customers", payload)
        cust_id = str(data.get("id") or "")
        if not cust_id:
            raise RuntimeError("Asaas returned no customer id")
        return cust_id

    def create_pix_charge(
        self,
        *,
        user_id: int,
        plan: str,
        amount: float,
        currency: str,
        customer_id: str,
        base_url: str,
        description: str,
    ) -> PaymentCreateResult:
        if currency.upper() != "BRL":
            raise ValueError("Asaas PIX is only for BRL")

        # Asaas expects value as decimal number in BRL
        payload = {
            "customer": customer_id,
            "billingType": "PIX",
            "value": float(amount),
            # for PIX, dueDate is required in many setups; set today+1
            "dueDate": (datetime.utcnow().date() + timedelta(days=1)).isoformat(),
            "description": description,
            "externalReference": f"tg:{user_id}:{plan}",
        }
        payment = self._post("/v3/payments", payload)
        external_id = str(payment.get("id") or "")
        invoice_url = payment.get("invoiceUrl")

        pix = self._get(f"/v3/payments/{external_id}/pixQrCode")
        # Fields observed in docs: payload (copy/paste), encodedImage (base64 PNG)
        pix_payload = pix.get("payload") or pix.get("qrCode") or pix.get("copyPaste") or ""
        encoded = pix.get("encodedImage") or pix.get("image") or ""
        png_bytes = None
        if isinstance(encoded, str) and encoded:
            try:
                png_bytes = base64.b64decode(encoded)
            except Exception:
                png_bytes = None

        return PaymentCreateResult(
            provider="asaas",
            external_id=external_id,
            amount=amount,
            currency=currency,
            checkout_url=invoice_url,
            pix_qr_code=str(pix_payload) if pix_payload else None,
            pix_qr_code_png_bytes=png_bytes,
        )

    def get_payment_status(self, external_id: str) -> str:
        data = self._get(f"/v3/payments/{external_id}")
        return str(data.get("status") or "")

    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Fetch full payment details from Asaas.

        Useful for manual confirmation (A2). Returns the JSON dict.
        """
        data = self._get(f"/v3/payments/{payment_id}")
        if not isinstance(data, dict):
            raise RuntimeError("Asaas returned unexpected payload")
        return data

    def webhook_is_valid(self, headers: Dict[str, str], query: Dict[str, str]) -> bool:
        if not self.webhook_token:
            return True
        # Support either query token or header token
        token = (query.get("token") or headers.get("asaas-access-token") or headers.get("x-webhook-token") or "").strip()
        return token == self.webhook_token


class NowPaymentsClient:
    """Minimal NOWPayments wrapper for crypto payments (international fallback).

    Flow:
      - create payment via POST /v1/payment with ipn_callback_url
      - validate IPN webhook signature (HMAC SHA-512 over JSON.stringify(body, sorted keys))
      - treat payment as paid on status confirmed/finished/partially_paid
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("NOWPAYMENTS_API_KEY")
        self.ipn_secret = os.getenv("NOWPAYMENTS_IPN_SECRET") or ""
        # Required by NOWPayments: which cryptocurrency the user will pay with.
        # Examples: "xmr", "usdttrc20", "usdtbsc", "btc".
        self.pay_currency = (os.getenv("NOWPAYMENTS_PAY_CURRENCY") or os.getenv("NOWPAYMENTS_DEFAULT_PAY_CURRENCY") or "xmr").strip().lower()
        self.base_url = os.getenv("NOWPAYMENTS_BASE_URL", "https://api.nowpayments.io").rstrip("/")
        if not self.api_key:
            raise ValueError("NOWPAYMENTS_API_KEY is not set")

        self._session = requests.Session()
        self._session.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "viponlybot/1.0",
        })

    def create_payment(
        self,
        *,
        user_id: int,
        plan: str,
        amount: float,
        currency: str,
        base_url: str,
        order_description: str,
    ) -> PaymentCreateResult:
        # NOWPayments expects price_amount + price_currency; we keep price in fiat.
        ipn_url = base_url.rstrip("/") + "/webhooks/nowpayments"
        payload = {
            "price_amount": float(amount),
            "price_currency": currency.lower(),
            "pay_currency": self.pay_currency,
            "order_id": f"tg:{user_id}:{plan}",
            "order_description": order_description,
            "ipn_callback_url": ipn_url,
        }
        url = f"{self.base_url}/v1/payment"
        r = self._session.post(url, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"NOWPayments API error {r.status_code}: {r.text[:300]}")
        data = r.json()
        payment_id = str(data.get("payment_id") or data.get("paymentid") or "")
        checkout_url = data.get("invoice_url") or None

        # Some responses include pay_address + pay_amount; we store them in raw_payload in DB, and show to user.
        return PaymentCreateResult(
            provider="nowpayments",
            external_id=payment_id,
            amount=amount,
            currency=currency,
            checkout_url=checkout_url,
        )

    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/payment/{payment_id}"
        r = self._session.get(url, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"NOWPayments API error {r.status_code}: {r.text[:300]}")
        return r.json()

    @staticmethod
    def _stable_json_string(data: Dict[str, Any]) -> str:
        # Mimic JSON.stringify(params, Object.keys(params).sort())
        def _sort_obj(obj):
            if isinstance(obj, dict):
                return {k: _sort_obj(obj[k]) for k in sorted(obj.keys())}
            if isinstance(obj, list):
                return [_sort_obj(x) for x in obj]
            return obj
        sorted_obj = _sort_obj(data)
        return json.dumps(sorted_obj, separators=(",", ":"), ensure_ascii=False)

    def verify_ipn(self, payload: Dict[str, Any], signature_hex: str) -> bool:
        if not self.ipn_secret:
            # If secret isn't set, we cannot verify; treat as invalid for safety.
            return False
        msg = self._stable_json_string(payload).encode("utf-8")
        mac = hmac.new(self.ipn_secret.encode("utf-8"), msg=msg, digestmod=hashlib.sha512).hexdigest()
        return mac == (signature_hex or "").strip().lower()

    @staticmethod
    def is_paid_status(status: str) -> bool:
        s = (status or "").lower()
        return s in ("confirmed", "finished", "partially_paid")

def payment_provider_for(lang: str, currency: str) -> str:
    """Routing:
    - Brazil (pt or BRL) -> Asaas PIX
    - Otherwise -> Stripe
    """
    if currency.upper() == "BRL" or lang == "pt":
        return "asaas"
    return "stripe"



def create_payment_for_user(
    *,
    user_id: int,
    plan: str,
    lang: str,
    amount: float,
    currency: str,
    base_url: str,
) -> PaymentCreateResult:
    """Create a payment for a user.

    Primary routing:
      - pt/BRL -> Asaas PIX
      - others -> Stripe Checkout

    Fallback:
      - If Stripe returns "No valid payment method types..." and NOWPAYMENTS is configured,
        create a crypto payment via NOWPayments instead (provider=nowpayments).
    """
    provider = payment_provider_for(lang, currency)

    if provider == "asaas":
        # A2 flow: do NOT create a PIX charge via API (which may require CPF/CNPJ).
        # Instead, send the user to a pre-created Asaas Payment Link and later ask
        # them to paste the payment id (pay_...) for verification.
        link = get_asaas_pix_link(plan)
        if not link:
            raise RuntimeError("Asaas PIX link is not configured for this plan")
        external_id = f"asaaslink:{user_id}:{plan}:{int(time.time())}"
        return PaymentCreateResult(
            provider="asaas",
            external_id=external_id,
            amount=float(amount),
            currency=str(currency).upper(),
            checkout_url=link,
            raw_provider_payload={"link": link, "mode": "payment_link"},
        )

    # Stripe (default)
    try:
        client = StripeClient()
        return client.create_checkout_session(
            user_id=user_id,
            plan=plan,
            amount=amount,
            currency=currency,
            base_url=base_url,
            lang=lang,
        )
    except Exception as e:
        msg = str(e)
        # Specific known Stripe error when account/payment methods aren't enabled yet
        if ("No valid payment method types" in msg) or ("payment methods compatible" in msg):
            # Crypto fallback (optional)
            if os.getenv("NOWPAYMENTS_API_KEY"):
                np = NowPaymentsClient()
                # Create crypto payment priced in fiat (currency should be USD/EUR etc)
                payment = np.create_payment(
                    user_id=user_id,
                    plan=plan,
                    amount=amount,
                    currency=currency,
                    base_url=base_url,
                    order_description=f"VIP {plan}",
                )
                # Enrich with immediate details if present
                try:
                    raw = np.get_payment(payment.external_id)
                except Exception:
                    raw = None
                if isinstance(raw, dict):
                    payment.crypto_pay_address = raw.get("pay_address") or raw.get("payaddress")
                    try:
                        payment.crypto_pay_amount = float(raw.get("pay_amount") or raw.get("payamount") or 0) or None
                    except Exception:
                        payment.crypto_pay_amount = None
                    payment.crypto_pay_currency = raw.get("pay_currency") or raw.get("paycurrency")
                    payment.raw_provider_payload = raw
                return payment

        raise