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
        try:
            self.ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
        except (ValueError, TypeError):
            logger.warning("ADMIN_ID is not a valid integer. Defaulting to 0.")
            self.ADMIN_ID = 0

    def validate(self) -> bool:
        """Validate that essential configuration variables are set."""
        if not self.BOT_TOKEN:
            logger.critical("FATAL: BOT_TOKEN is not set in environment variables!")
            return False
        if not self.ADMIN_ID:
            logger.critical("FATAL: ADMIN_ID is not set or invalid in environment variables!")
            return False
        logger.info("Essential configuration validated successfully.")
        return True
