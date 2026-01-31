"""Offline final validation.

Rode:
  python app/final_validation_zero_erro.py
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


async def run_final_validation() -> None:
    print("🚀 INICIANDO VALIDAÇÃO FINAL (offline)\n")

    os.environ.setdefault("BOT_TOKEN", "TEST_TOKEN")
    os.environ.setdefault("ADMIN_ID", "12345")
    os.environ.setdefault("PUBLIC_URL", "https://example.com")

    from app.config import Config
    from app.users_db import UserDB
    from app.payments import payment_provider_for

    cfg = Config()
    assert cfg.validate() is True
    print("✅ Config.validate: OK")

    db_path = "zero_erro_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = UserDB(db_path)

    user_id = 67890
    db.update_user(
        user_id,
        username="rafa",
        first_name="Rafa",
        language="pt",
        is_god_mode=0,
        is_vip=0,
        daily_previews_used=0,
        last_preview_date=datetime.now().date().isoformat(),
    )
    u = db.get_user(user_id)
    assert u["user_id"] == user_id
    print("✅ DB update/get user: OK")

    # GOD mode toggle via update_user
    db.update_user(user_id, is_god_mode=1)
    assert db.get_user(user_id)["is_god_mode"] == 1
    db.update_user(user_id, is_god_mode=0)
    assert db.get_user(user_id)["is_god_mode"] == 0
    print("✅ GOD mode toggle: OK")

    # VIP flag toggle via update_user
    db.update_user(user_id, is_vip=1, license_type="vip", license_expiry=None)
    assert db.get_user(user_id)["is_vip"] == 1
    db.update_user(user_id, is_vip=0)
    assert db.get_user(user_id)["is_vip"] == 0
    print("✅ VIP flag toggle: OK")

    # Preview limits reset
    db.update_user(
        user_id,
        daily_previews_used=3,
        last_preview_date=(datetime.now() - timedelta(days=1)).date().isoformat(),
    )
    assert db.check_preview_limit(user_id) is True
    db.update_user(user_id, daily_previews_used=3, last_preview_date=datetime.now().date().isoformat())
    assert db.check_preview_limit(user_id) is False
    print("✅ Preview limit + reset: OK")

    # Payment routing (offline)
    assert payment_provider_for("pt", "BRL") == "asaas"
    assert payment_provider_for("en", "USD") == "stripe"
    print("✅ Payment routing: OK")

    print("\n🎉 VALIDAÇÃO FINAL OK (offline)")


if __name__ == "__main__":
    asyncio.run(run_final_validation())
