import sys
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmokeTest")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


async def test_imports_and_config() -> bool:
    logger.info("Testing module imports and config validation...")

    # Minimal env required by Config.validate()
    os.environ.setdefault("BOT_TOKEN", "TEST_TOKEN")
    os.environ.setdefault("ADMIN_ID", "123456")
    os.environ.setdefault("PUBLIC_URL", "https://example.com")

    try:
        from app.config import Config
        from app.payments import payment_provider_for
        from app.users_db import user_db  # noqa: F401

        cfg = Config()
        if not cfg.validate():
            logger.error("❌ Config validation failed.")
            return False

        # Payment routing sanity check (no network calls)
        assert payment_provider_for("pt", "BRL") == "asaas"
        assert payment_provider_for("en", "USD") == "stripe"
        assert payment_provider_for("es", "EUR") == "stripe"
        logger.info("✅ Imports + config + routing sanity check passed.")
        return True

    except Exception as e:
        logger.error(f"❌ Smoke test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    ok = asyncio.run(test_imports_and_config())
    if ok:
        logger.info("🚀 SMOKE TEST PASSED!")
        raise SystemExit(0)
    logger.error("💥 SMOKE TEST FAILED!")
    raise SystemExit(1)
