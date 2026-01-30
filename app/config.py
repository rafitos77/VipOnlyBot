"""
Configuration module - Senior Architecture
This module defines the Config class but does not instantiate it.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the bot. Reads from environment variables."""
    
    def __init__(self):
        logger.debug("Initializing Config object...")
        # Bot settings
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.STRIPE_API_TOKEN = os.getenv("STRIPE_API_TOKEN")
        self.PUSHINPAY_API_KEY = os.getenv("PUSHINPAY_API_KEY")
        self.PUSHINPAY_WEBHOOK_SECRET = os.getenv("PUSHINPAY_WEBHOOK_SECRET")
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL")
        try:
            self.ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
        except (ValueError, TypeError):
            logger.warning("ADMIN_ID is not a valid integer. Defaulting to 0.")
            self.ADMIN_ID = 0
            
        # Channel IDs
        try:
            self.VIP_CHANNEL_ID = int(os.getenv("VIP_CHANNEL_ID", 0))
        except:
            self.VIP_CHANNEL_ID = 0
            
        self.MAX_FILES_PER_BATCH = int(os.getenv("MAX_FILES_PER_BATCH", 10))
        
        # Outras configurações dinâmicas
        self._raw_config = os.environ.copy()

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a config value from environment"""
        return os.getenv(key, default)

    def get_sub_link_by_lang(self, lang: str) -> str:
        """Get subscription link for a language"""
        links = {
            'pt': os.getenv("SUB_LINK_PT", "https://t.me/YourBot"),
            'es': os.getenv("SUB_LINK_ES", "https://t.me/YourBot"),
            'en': os.getenv("SUB_LINK_EN", "https://t.me/YourBot")
        }
        return links.get(lang, links['en'])

    def validate(self) -> bool:
        """Validate that essential configuration variables are set."""
        missing = []
        if not self.BOT_TOKEN:
            missing.append("BOT_TOKEN")
        if not self.ADMIN_ID:
            missing.append("ADMIN_ID")

        # If Pushin Pay is configured for Pix, require webhook secret and webhook URL
        if self.PUSHINPAY_API_KEY or self.WEBHOOK_URL:
            if not self.PUSHINPAY_WEBHOOK_SECRET:
                missing.append("PUSHINPAY_WEBHOOK_SECRET")
            if not self.WEBHOOK_URL:
                missing.append("WEBHOOK_URL")

        if missing:
            logger.critical(f"FATAL: Missing or invalid environment variables: {', '.join(missing)}")
            return False

        # Basic format checks
        if self.WEBHOOK_URL and not (self.WEBHOOK_URL.startswith("https://") or self.WEBHOOK_URL.startswith("http://")):
            logger.warning("WEBHOOK_URL does not appear to be a valid URL (should start with http:// or https://).")

        logger.info("Essential configuration validated successfully.")
        return True
