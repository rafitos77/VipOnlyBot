import os
import logging
import hmac
import hashlib
import json
from typing import Optional, Dict, Any
import aiohttp
import asyncio

from app.config import Config
config = Config()

logger = logging.getLogger(__name__)


class PushinPayClient:
    """Async client for Pushin Pay API using aiohttp.
    Replaces blocking requests calls so it doesn't stall the event loop.
    """

    def __init__(self):
        self.api_key = os.getenv("PUSHINPAY_API_KEY")
        self.webhook_secret = os.getenv("PUSHINPAY_WEBHOOK_SECRET")
        self.base_url = "https://api.pushinpay.com/v1"
        # Default timeout
        self._timeout = aiohttp.ClientTimeout(total=30)

    async def create_pix_charge(self, amount: float, reference_id: str, webhook_url: str) -> Optional[Dict[str, Any]]:
        """Create a Pix charge asynchronously."""
        url = f"{self.base_url}/charges"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "amount": int(amount * 100),  # amount in cents
            "currency": "BRL",
            "reference_id": reference_id,
            "webhook_url": webhook_url
        }

        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    text = await resp.text()
                    if resp.status == 200:
                        return await resp.json()
                    logger.error(f"Pushin Pay Charge Error: {resp.status} - {text}")
                    return None
        except asyncio.TimeoutError:
            logger.error("Pushin Pay create_pix_charge timed out")
            return None
        except Exception as e:
            logger.error(f"Pushin Pay Charge Exception: {e}")
            return None

    def verify_webhook_signature(self, signature: str, payload: bytes) -> bool:
        """Verify webhook signature using HMAC-SHA256."""
        try:
            if not self.webhook_secret:
                logger.error("No webhook secret configured for Pushin Pay")
                return False
            expected_signature = hmac.new(self.webhook_secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Pushin Pay Webhook Signature Verification Exception: {e}")
            return False

    async def get_charge_status(self, charge_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a Pix charge asynchronously."""
        url = f"{self.base_url}/charges/{charge_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            async with aiohttp.ClientSession(timeout=self._timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    text = await resp.text()
                    if resp.status == 200:
                        return await resp.json()
                    logger.error(f"Pushin Pay Get Charge Error: {resp.status} - {text}")
                    return None
        except asyncio.TimeoutError:
            logger.error("Pushin Pay get_charge_status timed out")
            return None
        except Exception as e:
            logger.error(f"Pushin Pay Get Charge Exception: {e}")
            return None


# Global instance (callers will await async methods)
pushinpay_client = PushinPayClient()