"""Offline integration tests.

Covers:
- Telegram UI helper safe_edit_or_send fallback
- Pagination next offset computation
- Uploader: no parse_mode for media captions, handles special chars, skips empty/oversize
- DB: user creation, GOD toggle, VIP flag evaluation

Usage:
  python integration_test.py
"""

import asyncio
import logging
import os
import tempfile
import unittest
from unittest.mock import AsyncMock

# --- Optional dependency stub ---
# These tests are designed to run offline. If python-telegram-bot isn't installed in the
# current environment, we inject a minimal stub that satisfies imports and allows unit tests
# to validate our own logic (e.g., "no parse_mode in media send" and safe_edit fallback).
try:
    import telegram  # type: ignore
except Exception:  # pragma: no cover
    import types
    import sys as _sys

    telegram = types.ModuleType("telegram")
    telegram_error = types.ModuleType("telegram.error")
    telegram_constants = types.ModuleType("telegram.constants")

    class BadRequest(Exception):
        pass

    class TelegramError(Exception):
        pass

    class RetryAfter(Exception):
        def __init__(self, retry_after: int = 1):
            self.retry_after = retry_after

    class TimedOut(Exception):
        pass

    class ParseMode:
        MARKDOWN = "Markdown"

    # Minimal types used by uploader
    class Bot:
        pass

    class InputMediaPhoto:
        def __init__(self, media, caption=None):
            self.media = media
            self.caption = caption

    class InputMediaVideo:
        def __init__(self, media, caption=None):
            self.media = media
            self.caption = caption

    telegram.Bot = Bot
    telegram.InputMediaPhoto = InputMediaPhoto
    telegram.InputMediaVideo = InputMediaVideo

    telegram_error.BadRequest = BadRequest
    telegram_error.TelegramError = TelegramError
    telegram_error.RetryAfter = RetryAfter
    telegram_error.TimedOut = TimedOut

    telegram_constants.ParseMode = ParseMode

    _sys.modules["telegram"] = telegram
    _sys.modules["telegram.error"] = telegram_error
    _sys.modules["telegram.constants"] = telegram_constants

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integration_test")


def _prepare_env(tmp_db: str):
    os.environ.setdefault("BOT_TOKEN", "123456789:ABCDEF-GHIJKL-MNOPQRSTUV")
    os.environ.setdefault("ADMIN_ID", "12345678")
    os.environ["DB_PATH"] = tmp_db
    os.environ.setdefault("TELEGRAM_MAX_UPLOAD_MB", "1")


class TestTelegramHelpers(unittest.IsolatedAsyncioTestCase):
    async def test_safe_edit_or_send_fallback(self):
        from telegram.error import BadRequest
        from app.telegram_helpers import safe_edit_or_send

        bot = AsyncMock()
        query = AsyncMock()
        query.edit_message_text.side_effect = BadRequest("cannot edit")
        # minimal message with chat_id
        query.message.chat_id = 111
        query.from_user.id = 222

        edited = await safe_edit_or_send(bot, query, "hi")
        self.assertFalse(edited)
        bot.send_message.assert_awaited()

    def test_next_post_offset(self):
        from app.telegram_helpers import next_post_offset
        self.assertEqual(next_post_offset(0, 50), 50)
        self.assertEqual(next_post_offset(100, 0), 100)


class TestUploader(unittest.IsolatedAsyncioTestCase):
    async def test_uploader_no_parse_mode_in_media(self):
        from app.uploader import TelegramUploader

        bot = AsyncMock()
        uploader = TelegramUploader(bot)

        # create temp file
        fd, path = tempfile.mkstemp(suffix=".jpg")
        os.write(fd, b"123")
        os.close(fd)

        class DummyItem:
            local_path = path
            media_type = "photo"
            post_id = "p1"

        ok = await uploader.upload_and_cleanup(DummyItem(), 999, caption="name_with_underscore_ and [brackets]")
        self.assertTrue(ok)

        # send_photo should be called without parse_mode
        _, kwargs = bot.send_photo.await_args
        self.assertNotIn("parse_mode", kwargs)

    async def test_uploader_skips_empty_and_large(self):
        from app.uploader import TelegramUploader

        bot = AsyncMock()
        uploader = TelegramUploader(bot)
        os.environ["TELEGRAM_MAX_UPLOAD_MB"] = "0"  # force oversize for any >0 file

        # empty file
        fd, empty_path = tempfile.mkstemp(suffix=".mp4")
        os.close(fd)

        class DummyEmpty:
            local_path = empty_path
            media_type = "video"
            post_id = "p2"

        ok1 = await uploader.upload_and_cleanup(DummyEmpty(), 999, caption="x")
        self.assertFalse(ok1)
        self.assertGreaterEqual(uploader.stats.skipped_empty, 1)

        # non-empty but 'oversize'
        fd, big_path = tempfile.mkstemp(suffix=".mp4")
        os.write(fd, b"1")
        os.close(fd)

        class DummyBig:
            local_path = big_path
            media_type = "video"
            post_id = "p3"

        ok2 = await uploader.upload_and_cleanup(DummyBig(), 999, caption="x")
        self.assertFalse(ok2)
        self.assertGreaterEqual(uploader.stats.skipped_large, 1)


class TestUserDB(unittest.TestCase):
    def test_user_creation_and_toggles(self):
        fd, tmp_db = tempfile.mkstemp(prefix="bot_it_db_", suffix=".sqlite")
        os.close(fd)
        if os.path.exists(tmp_db):
            os.remove(tmp_db)
        _prepare_env(tmp_db)

        from app.users_db import UserDB

        db = UserDB(db_path=tmp_db)
        u = db.get_user(42)
        self.assertEqual(u["user_id"], 42)
        self.assertIn("is_god_mode", u)

        # base: not VIP
        self.assertFalse(db.is_license_active(42))

        # toggle god mode -> VIP effective
        db.update_user(42, is_god_mode=1)
        self.assertTrue(db.is_license_active(42))

        # vip flag also enables
        db.update_user(42, is_god_mode=0, is_vip=1)
        self.assertTrue(db.is_license_active(42))


if __name__ == "__main__":
    # Ensure env prepared for imports that read at module import time.
    tmp_db = os.path.join(tempfile.gettempdir(), "bot_integration_test.db")
    _prepare_env(tmp_db)
    unittest.main(verbosity=2)
