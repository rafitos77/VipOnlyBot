"""Offline smoke test for the Telegram VIP bot.

Runs (offline):
- Basic imports
- Config validation
- Payment routing sanity
- DB initialization using a temporary SQLite file

Usage:
  python smoke_test.py
"""

import asyncio
import logging
import os
import sys
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smoke_test")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _prepare_env() -> str:
    os.environ.setdefault("BOT_TOKEN", "123456789:ABCDEF-GHIJKL-MNOPQRSTUV")
    os.environ.setdefault("ADMIN_ID", "12345678")
    tmp_db = os.path.join(tempfile.gettempdir(), "bot_smoke_test.db")
    os.environ["DB_PATH"] = tmp_db
    return tmp_db


async def main() -> int:
    tmp_db = _prepare_env()
    logger.info("Using temp DB: %s", tmp_db)

    # Imports
    from app.config import Config
    from app.payments import payment_provider_for
    from app.users_db import UserDB

    cfg = Config()
    assert cfg.validate(), "Config validation failed"

    assert payment_provider_for("pt", "BRL") == "asaas"
    assert payment_provider_for("en", "USD") == "stripe"

    # DB init
    db = UserDB(db_path=tmp_db)
    u = db.get_user(999)
    assert u["user_id"] == 999

    logger.info("✅ Smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
