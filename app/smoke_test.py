import sys
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmokeTest")

# Mock environment variables
os.environ["BOT_TOKEN"] = "123456789:ABCDEF-GHIJKL-MNOPQRSTUV"
os.environ["ADMIN_ID"] = "12345678"

async def test_imports():
    logger.info("Testing module imports...")
    try:
        from app.config import Config
        from users_db import user_db
        from smart_search import smart_search
        from paypal_integration import paypal_client
        logger.info("✅ Basic imports successful.")
        
        config = Config()
        if config.validate():
            logger.info("✅ Config validation successful.")
        else:
            logger.error("❌ Config validation failed.")
            return False
            
        return True
    except Exception as e:
        logger.error(f"❌ Import test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_imports())
    if success:
        logger.info("🚀 SMOKE TEST PASSED!")
        sys.exit(0)
    else:
        logger.error("💥 SMOKE TEST FAILED!")
        sys.exit(1)
