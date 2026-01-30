"""
app.payments

Unified payment layer.

Providers
- Stripe: international payments via Stripe Checkout Sessions.
- PushinPay: Brazil PIX via PushinPay PIX CashIn.

Public API
- create_payment_for_user(...)

The bot runs Telegram polling. To auto-activate VIP after payment, the bot also
runs an embedded aiohttp web server (see app.main) for webhooks.
"""

from __future__ import annotations

import base64
import logging
import os
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
    # PushinPay extras
    pix_qr_code: Optional[str] = None
    pix_qr_code_png_bytes: Optional[bytes] = None


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


class PushinPayClient:
    """
    Minimal PushinPay wrapper for PIX CashIn.

    Docs mention:
    - POST /pix/cashIn creates PIX charge, values in centavos, may include webhook_url
    - Webhook payload includes: id, value, status (created|paid|canceled), etc.
    """
    def __init__(self) -> None:
        self.api_key = os.getenv("PUSHINPAY_TOKEN")
        self.base_url = os.getenv("PUSHINPAY_BASE_URL", "https://api.pushinpay.com.br")
        # Optional: token you append to the webhook URL so you can validate source
        self.webhook_token = os.getenv("PUSHINPAY_WEBHOOK_TOKEN")

        if not self.api_key:
            raise ValueError("PUSHINPAY_TOKEN is not set")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def create_pix(
        self,
        *,
        user_id: int,
        plan: str,
        amount_brl: float,
        base_url: str,
    ) -> PaymentCreateResult:
        value_centavos = int(round(amount_brl * 100))
        webhook_url = None
        if base_url:
            webhook_url = base_url.rstrip("/") + "/webhooks/pushinpay"
            if self.webhook_token:
                webhook_url += f"?token={self.webhook_token}"

        payload: Dict[str, Any] = {"value": value_centavos}
        if webhook_url:
            payload["webhook_url"] = webhook_url

        url = self.base_url.rstrip("/") + "/pix/cashIn"
        resp = requests.post(url, json=payload, headers=self._headers(), timeout=20)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"PushinPay cashIn failed: {resp.status_code} {resp.text}")

        data = resp.json()
        pix_code = data.get("qr_code")
        qrcode_base64 = data.get("qr_code_base64")

        png_bytes = None
        if isinstance(qrcode_base64, str) and "base64," in qrcode_base64:
            b64 = qrcode_base64.split("base64,", 1)[1]
            try:
                png_bytes = base64.b64decode(b64)
            except Exception:
                png_bytes = None

        return PaymentCreateResult(
            provider="pushinpay",
            external_id=str(data.get("id")),
            amount=amount_brl,
            currency="BRL",
            pix_qr_code=pix_code,
            pix_qr_code_png_bytes=png_bytes,
        )

    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        url = self.base_url.rstrip("/") + f"/transaction/{transaction_id}"
        resp = requests.get(url, headers=self._headers(), timeout=20)
        if resp.status_code != 200:
            raise RuntimeError(f"PushinPay transaction lookup failed: {resp.status_code} {resp.text}")
        return resp.json()


def payment_provider_for(lang: str, currency: str) -> str:
    """
    Routing rule requested:
    - Brazil -> PushinPay
    - International -> Stripe

    In this project, BRL currency is treated as Brazil.
    """
    if currency.upper() == "BRL" or lang == "pt":
        return "pushinpay"
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
    provider = payment_provider_for(lang, currency)

    if provider == "pushinpay":
        client = PushinPayClient()
        return client.create_pix(user_id=user_id, plan=plan, amount_brl=amount, base_url=base_url)
    else:
        client = StripeClient()
        return client.create_checkout_session(
            user_id=user_id,
            plan=plan,
            amount=amount,
            currency=currency,
            base_url=base_url,
            lang=lang,
        )
