"""Telegram helper utilities.

These utilities are intentionally small and dependency-light so they can be unit-tested offline.

Project rules:
- NEVER use parse_mode for media captions.
- Parse modes are allowed for TEXT messages only. Dynamic user-provided strings must be escaped.
"""

from __future__ import annotations

import logging
from typing import Optional

from telegram.error import BadRequest

logger = logging.getLogger(__name__)


def escape_markdown(text: Optional[str]) -> str:
    """Escape minimal Markdown characters for ParseMode.MARKDOWN.

    This is *not* MarkdownV2. It is intended for short dynamic inserts.
    """
    if text is None:
        return ""
    s = str(text)
    for ch in ["_", "*", "[", "]", "(", ")", "`"]:
        s = s.replace(ch, f"\\{ch}")
    return s


async def safe_edit_or_send(bot, query, text: str, reply_markup=None, parse_mode=None) -> bool:
    """Try editing the message associated with a CallbackQuery.

    Falls back to bot.send_message if the edit fails (common BadRequest reasons: message too old,
    message not modified, cannot edit, etc.).

    Returns True if edited, False if fallback send.
    """
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
        return True
    except BadRequest as e:
        logger.warning("UI edit failed (BadRequest): %s", e)
        try:
            chat_id = query.message.chat_id if getattr(query, "message", None) else query.from_user.id
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception as e2:
            logger.error("UI fallback send failed: %s", e2)
        return False


def next_post_offset(current_offset: int, posts_count: int) -> int:
    """Compute next offset for APIs that paginate by posts."""
    if posts_count <= 0:
        return current_offset
    return int(current_offset) + int(posts_count)
