import sys
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmokeTest")

# Ensure project root is on sys.path so `import app.*` works even when executing
# this file directly (python app/smoke_test.py).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Mock environment variables
os.environ["BOT_TOKEN"] = "123456789:ABCDEF-GHIJKL-MNOPQRSTUV"
os.environ["ADMIN_ID"] = "12345678"

async def test_imports():
    logger.info("Testing module imports...")
    try:
        from app.config import Config
        from app.users_db import user_db
        from app.smart_search import smart_search
        from app.payments import payment_provider_for
        logger.info("✅ Basic imports successful.")
        
        config = Config()
        if config.validate():
            logger.info("✅ Config validation successful.")
        else:
            logger.error("❌ Config validation failed.")
            return False
            
        # Quick payment routing sanity check
        assert payment_provider_for("pt", "BRL") == "pushinpay"
        assert payment_provider_for("en", "USD") == "stripe"
        logger.info("✅ Payment routing sanity check passed.")
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
