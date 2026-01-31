"""Offline tests for payment-method selection logic.

These tests don't call external APIs. They validate:
  - availability gates via env vars
  - Stripe 'no payment method types' error detection
  - language strings existence

Run:
  python app/gateway_selection_test.py
"""

import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main() -> int:
    from app.payments import (
        stripe_available,
        asaas_available,
        nowpayments_available,
        is_stripe_no_payment_methods_error,
    )
    from app.languages import get_text

    # Ensure language strings exist
    for lang in ("pt", "en", "es"):
        for key in ("btn_pay_crypto", "payment_choose_method", "payment_no_methods", "stripe_unavailable", "pix_unavailable", "payment_created_pix_link", "btn_open_payment_link", "btn_confirm_payment", "payment_prompt_asaas_id", "payment_invalid_asaas_id", "payment_cancelled", "payment_already_used", "payment_not_pix", "payment_amount_mismatch"):
            _ = get_text(key, lang)

    # Availability flags
    os.environ.pop("STRIPE_SECRET_KEY", None)
    os.environ.pop("ASAAS_ACCESS_TOKEN", None)
    os.environ.pop("NOWPAYMENTS_API_KEY", None)
    os.environ.pop("NOWPAYMENTS_IPN_SECRET", None)

    assert stripe_available() is False
    assert asaas_available() is False
    assert nowpayments_available() is False

    os.environ["STRIPE_SECRET_KEY"] = "sk_test_x"
    assert stripe_available() is True

    os.environ["ASAAS_ACCESS_TOKEN"] = "asaas_x"
    os.environ["ASAAS_PIX_LINK_MONTHLY"] = "https://example.com/pix"
    assert asaas_available() is True


    # NOWPayments should be offered if API key exists (IPN secret is recommended but not required to show CTA)
    os.environ["NOWPAYMENTS_API_KEY"] = "np_x"
    if "NOWPAYMENTS_IPN_SECRET" in os.environ:
        del os.environ["NOWPAYMENTS_IPN_SECRET"]
    assert nowpayments_available() is True

    os.environ["NOWPAYMENTS_IPN_SECRET"] = "np_secret"
    assert nowpayments_available() is True

    # Stripe error detection should be strict
    assert is_stripe_no_payment_methods_error(Exception("No valid payment method types for this Checkout Session"))
    assert is_stripe_no_payment_methods_error(Exception("payment methods compatible"))
    assert not is_stripe_no_payment_methods_error(Exception("Invalid URL"))

    print("OK - gateway selection tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
