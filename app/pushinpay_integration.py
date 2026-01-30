import os
import logging
import requests
import hmac
import hashlib
import json
from typing import Optional, Dict, Any

from app.config import Config
config = Config()

logger = logging.getLogger(__name__)

class PushinPayClient:
    """Client for Pushin Pay API"""

    def __init__(self):
        self.api_key = os.getenv("PUSHINPAY_API_KEY")
        self.webhook_secret = os.getenv("PUSHINPAY_WEBHOOK_SECRET")
        self.base_url = "https://api.pushinpay.com/v1" # This might be subject to change, use their documentation.

    def create_pix_charge(self, amount: float, reference_id: str, webhook_url: str) -> Optional[Dict[str, Any]]:
        """Create a Pix charge with Pushin Pay"""
        try:
            url = f"{self.base_url}/charges"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "amount": int(amount * 100), # Pushin Pay usually expects amount in cents
                "currency": "BRL",
                "reference_id": reference_id,
                "webhook_url": webhook_url
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Pushin Pay Charge Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Pushin Pay Charge Exception: {e}")
            return None

    def verify_webhook_signature(self, signature: str, payload: bytes) -> bool:
        """Verify the webhook signature from Pushin Pay"""
        try:
            expected_signature = hmac.new(self.webhook_secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Pushin Pay Webhook Signature Verification Exception: {e}")
            return False

    def get_charge_status(self, charge_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a Pix charge"""
        try:
            url = f"{self.base_url}/charges/{charge_id}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Pushin Pay Get Charge Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Pushin Pay Get Charge Exception: {e}")
            return None

# Global instance
pushinpay_client = PushinPayClient()