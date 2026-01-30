"""
PayPal Integration Module
Handles order creation and payment verification
"""

import os
import logging
import requests
from typing import Optional, Dict, Any
from app.config import Config
config = Config()

logger = logging.getLogger(__name__)

class PayPalClient:
    """Client for PayPal REST API v2"""
    
    def __init__(self):
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        self.mode = os.getenv("PAYPAL_MODE", "sandbox") # sandbox or live
        
        if self.mode == "live":
            self.base_url = "https://api-m.paypal.com"
        else:
            self.base_url = "https://api-m.sandbox.paypal.com"
            
        self._access_token = None

    def _get_access_token(self) -> Optional[str]:
        """Get OAuth2 access token"""
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            headers = {"Accept": "application/json", "Accept-Language": "en_US"}
            data = {"grant_type": "client_credentials"}
            
            response = requests.post(
                url, 
                auth=(self.client_id, self.client_secret), 
                headers=headers, 
                data=data
            )
            
            if response.status_code == 200:
                self._access_token = response.json().get("access_token")
                return self._access_token
            else:
                logger.error(f"PayPal Auth Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"PayPal Auth Exception: {e}")
            return None

    def create_order(self, amount: float, currency: str, return_url: str, cancel_url: str) -> Optional[Dict[str, Any]]:
        """Create a PayPal order"""
        token = self._get_access_token()
        if not token:
            return None
            
        try:
            url = f"{self.base_url}/v2/checkout/orders"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}"
                    }
                }],
                "application_context": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                    "user_action": "PAY_NOW"
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"PayPal Order Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"PayPal Order Exception: {e}")
            return None

    def capture_payment(self, order_id: str) -> bool:
        """Capture payment for an approved order"""
        token = self._get_access_token()
        if not token:
            return False
            
        try:
            url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            response = requests.post(url, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return data.get("status") == "COMPLETED"
            else:
                logger.error(f"PayPal Capture Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"PayPal Capture Exception: {e}")
            return False

# Global instance
paypal_client = PayPalClient()
