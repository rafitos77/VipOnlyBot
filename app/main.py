
"""
Main bot module - v8.3 Global Edition
Telegram VIP Media Bot - Forbidden Access Portal
"""

import logging
import asyncio
import os
import sys
import random
import re
import json
from datetime import datetime
import fcntl

# Configure logging
logger = logging.getLogger(__name__)

async def run_bot():
    """
    Main entry point for the bot.
    """
    logger.info("🚀 Starting Bot in v8.3 Global Mode...")
    
    try:
        # Package imports
        from app.config import Config
        from app.fetcher import MediaFetcher
        from app.uploader import TelegramUploader
        from app.languages import get_text
        from app.users_db import user_db
        from app.smart_search import smart_search
        from app.payments import (
            create_payment_for_user,
            create_payment_explicit,
            payment_provider_for,
            stripe_available,
            asaas_available,
            nowpayments_available,
            nowpayments_allowed_for_plan,
            is_stripe_no_payment_methods_error,
        )
        from app.payments import AsaasClient, NowPaymentsClient

        
        # Telegram Libraries
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
        from telegram.ext import (
            Application,
            CommandHandler,
            ContextTypes,
            CallbackQueryHandler,
            MessageHandler,
            filters
        )
        from telegram.constants import ParseMode
        from telegram.error import BadRequest
        from aiohttp import web
        
        config = Config()
        if not config.validate():
            logger.critical("❌ Configuration validation failed.")
            return

        class VIPBotUltra:
            def __init__(self, app_instance, uploader_instance):
                self.app = app_instance
                self.uploader = uploader_instance
                # Secret models for visual impact
                self.big_three = ["hannaowo", "belledelphine", "sophierain"]

            def get_main_keyboard(self, user_id, lang):
                """Generate the main persistent GUI keyboard"""
                is_admin = (user_id == config.ADMIN_ID)
                u_data = user_db.get_user(user_id)
                
                keyboard = [
                    [KeyboardButton(get_text("btn_search", lang)), KeyboardButton(get_text("btn_vip", lang))],
                    [KeyboardButton(get_text("btn_share", lang)), KeyboardButton(get_text("btn_stats", lang))],
                    [KeyboardButton(get_text("btn_lang", lang)), KeyboardButton(get_text("btn_help", lang))]
                ]
                
                if is_admin:
                    god_status = get_text("god_mode_on" if int(u_data.get('is_god_mode', 0)) == 1 else "god_mode_off", lang)
                    keyboard.append([KeyboardButton(get_text("btn_god_mode", lang, status=god_status))])
                
                return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            def _esc_md(self, s: str) -> str:
                """Escape Markdown (legacy) special chars to avoid Telegram BadRequest.

                We only use ParseMode for TEXT messages; media captions must never use parse_mode.
                """
                if s is None:
                    return ""
                for ch in ["_", "*", "[", "]", "(", ")", "`"]:
                    s = s.replace(ch, f"\\{ch}")
                return s

            async def safe_edit_or_send(self, query, text, reply_markup=None, parse_mode=None):
                """Safely edit a callback message; fallback to sending a new message.

                This prevents UI/callback crashes (BadRequest) from killing the handler.
                """
                try:
                    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
                    return True
                except BadRequest as e:
                    logger.warning(f"UI edit failed (BadRequest): {e}")
                    try:
                        chat_id = query.message.chat_id if query.message else query.from_user.id
                        await self.app.bot.send_message(
                            chat_id=chat_id,
                            text=text,
                            reply_markup=reply_markup,
                            parse_mode=parse_mode,
                        )
                        return False
                    except Exception as e2:
                        logger.error(f"UI fallback send failed: {e2}")
                        return False

            # Backward-compatible alias
            async def safe_edit(self, query, text, reply_markup=None, parse_mode=None):
                return await self.safe_edit_or_send(query, text, reply_markup=reply_markup, parse_mode=parse_mode)




            async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                user = update.effective_user
                u_data = user_db.get_user(user.id)
                msg = update.effective_message
                
                # Handle Referral
                if context.args and context.args[0].startswith('ref'):
                    try:
                        referrer_id = int(context.args[0].replace('ref', ''))
                        if referrer_id != user.id:
                            user_db.process_referral(user.id, referrer_id)
                            try:
                                ref_data = user_db.get_user(referrer_id)
                                ref_lang = ref_data.get('language', 'pt')
                                await self.app.bot.send_message(
                                    chat_id=referrer_id,
                                    text=get_text("referral_reward_msg", ref_lang),
                                    parse_mode=ParseMode.MARKDOWN
                                )
                            except: pass
                    except: pass

                # Language Selection
                if not u_data.get('language') or (context.args and 'lang' in context.args):
                    keyboard = [
                        [InlineKeyboardButton("🇧🇷 Português", callback_data="setlang:pt")],
                        [InlineKeyboardButton("🇪🇸 Español", callback_data="setlang:es")],
                        [InlineKeyboardButton("🇺🇸 English", callback_data="setlang:en")]
                    ]
                    await msg.reply_text(
                        get_text("select_lang"), 
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    lang = u_data.get('language', 'pt')
                    welcome_title = get_text("welcome_title", lang, name=user.first_name)
                    welcome_copy = get_text("welcome_copy", lang)
                    
                    # Visual Welcome: Secret Media Search
                    status_msg = await msg.reply_text("🔄 " + get_text("loading", lang))
                    
                    try:
                        target = random.choice(self.big_three)
                        async with asyncio.timeout(15):
                            async with MediaFetcher() as fetcher:
                                creators = await fetcher._get_creators_list()
                                # Enhanced search logic
                                matches = []
                                for c in creators:
                                    if target in c.get('name', '').lower().replace(' ', ''):
                                        matches.append(c)
                                
                                if matches:
                                    creator = matches[0]
                                    items = await fetcher.fetch_posts_paged(creator, offset=0)
                                    if items:
                                        photos = [i for i in items if i.media_type == 'photo']
                                        pick = random.choice(photos[:5]) if photos else items[0]
                                        if await fetcher.download_media(pick):
                                            await status_msg.delete()
                                            await self.uploader.upload_and_cleanup(
                                                pick, user.id, 
                                                caption=f"{welcome_title}\n\n{welcome_copy}",
                                                reply_markup=self.get_main_keyboard(user.id, lang)
                                            )
                                            return
                    except Exception as e:
                        logger.error(f"Visual welcome failed: {e}")
                    
                    # Fallback to text only
                    try:
                        await status_msg.edit_text(
                            f"{welcome_title}\n\n{welcome_copy}",
                            reply_markup=self.get_main_keyboard(user.id, lang),
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        await msg.reply_text(
                            f"{welcome_title}\n\n{welcome_copy}",
                            reply_markup=self.get_main_keyboard(user.id, lang),
                            parse_mode=ParseMode.MARKDOWN
                        )

            async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                user_id = update.effective_user.id
                text = update.message.text
                if not text: return
                
                u_data = user_db.get_user(user_id)
                lang = u_data.get('language', 'pt')

                # A2 manual Asaas confirmation flow: user pastes payment id.
                if context.user_data.get("state") == "awaiting_asaas_payment_id":
                    raw = (text or "").strip()
                    if raw.lower() in ("/cancel", "cancelar", "cancel", "stop"):
                        context.user_data.pop("state", None)
                        context.user_data.pop("asaas_expected_plan", None)
                        context.user_data.pop("asaas_expected_amount", None)
                        await update.message.reply_text(get_text("payment_cancelled", lang))
                        return

                    # Extract payment id from text or URL (e.g., pay_xxx)
                    m_id = re.search(r"(pay_[A-Za-z0-9]+)", raw)
                    payment_id = (m_id.group(1) if m_id else raw).strip()

                    if not re.fullmatch(r"[A-Za-z0-9_\-]{8,80}", payment_id):
                        await update.message.reply_text(get_text("payment_invalid_asaas_id", lang))
                        return

                    if not os.getenv("ASAAS_ACCESS_TOKEN"):
                        await update.message.reply_text(get_text("pix_unavailable", lang))
                        return

                    expected_plan = str(context.user_data.get("asaas_expected_plan") or "monthly")
                    expected_amount = float(context.user_data.get("asaas_expected_amount") or 0.0)

                    try:
                        existing = user_db.get_payment_by_external_id("asaas", payment_id)
                        if existing and int(existing.get("user_id")) != user_id:
                            await update.message.reply_text(get_text("payment_already_used", lang))
                            return

                        if user_db.is_payment_already_paid("asaas", payment_id):
                            await update.message.reply_text(get_text("payment_confirmed", lang))
                            # Clear state
                            context.user_data.pop("state", None)
                            context.user_data.pop("asaas_expected_plan", None)
                            context.user_data.pop("asaas_expected_amount", None)
                            return

                        client = AsaasClient()
                        details = client.get_payment_details(payment_id)
                        status = str(details.get("status") or "").upper()
                        value = float(details.get("value") or 0.0)
                        billing_type = str(details.get("billingType") or "").upper()

                        if billing_type and billing_type != "PIX":
                            await update.message.reply_text(get_text("payment_not_pix", lang))
                            return

                        paid = status in ("RECEIVED", "CONFIRMED", "RECEIVED_IN_CASH")
                        if not paid:
                            await update.message.reply_text(get_text("payment_pending", lang))
                            return

                        if expected_amount > 0 and abs(value - expected_amount) > 0.02:
                            await update.message.reply_text(get_text("payment_amount_mismatch", lang))
                            return

                        raw_payload = json.dumps(details)[:4000]
                        user_db.create_pending_payment(
                            user_id=user_id,
                            provider="asaas",
                            external_id=payment_id,
                            amount=value or expected_amount,
                            currency="BRL",
                            plan_type=expected_plan,
                            raw_payload=raw_payload,
                        )
                        user_db.mark_payment_paid("asaas", payment_id, raw_payload=raw_payload)
                        user_db.activate_license(user_id, expected_plan)

                        # Clear state
                        context.user_data.pop("state", None)
                        context.user_data.pop("asaas_expected_plan", None)
                        context.user_data.pop("asaas_expected_amount", None)

                        await update.message.reply_text(get_text("payment_confirmed", lang))
                        return

                    except Exception:
                        logger.exception("Asaas manual confirmation failed")
                        await update.message.reply_text(get_text("payment_check_failed", lang))
                        return

                if text == get_text("btn_search", lang):

                    await update.message.reply_text(get_text("search_prompt", lang), parse_mode=ParseMode.MARKDOWN)
                    context.user_data['state'] = 'searching'
                
                elif text == get_text("btn_vip", lang):
                    await self.show_payment_popup(update, user_id, lang)

                elif text == get_text("btn_share", lang):
                    bot_username = (await context.bot.get_me()).username
                    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
                    await update.message.reply_text(
                        get_text("referral_copy", lang, link=ref_link, count=u_data.get('referral_count', 0), credits=u_data.get('credits', 0)),
                        parse_mode=ParseMode.MARKDOWN
                    )
                
                elif text == get_text("btn_stats", lang):
                    is_vip = "✅ VIP" if user_db.is_license_active(user_id) else "❌ FREE"
                    stats = f"👤 **{update.effective_user.first_name}**\n\n"
                    stats += f"Status: {is_vip}\n"
                    stats += f"Créditos: {u_data.get('credits', 0)}\n"
                    stats += f"Convidados: {u_data.get('referral_count', 0)}"
                    await update.message.reply_text(stats, parse_mode=ParseMode.MARKDOWN)
                
                elif text == get_text("btn_lang", lang):
                    keyboard = [[InlineKeyboardButton("🇧🇷 PT", callback_data="setlang:pt"), InlineKeyboardButton("🇪🇸 ES", callback_data="setlang:es"), InlineKeyboardButton("🇺🇸 EN", callback_data="setlang:en")]]
                    await update.message.reply_text(get_text("select_lang", lang), reply_markup=InlineKeyboardMarkup(keyboard))
                
                elif text == get_text("btn_help", lang):
                    await update.message.reply_text(get_text("welcome_copy", lang), parse_mode=ParseMode.MARKDOWN)
                
                elif text.startswith("⚡ MODO GOD") and user_id == config.ADMIN_ID:
                    current_status = int(u_data.get('is_god_mode', 0))
                    new_status = 0 if current_status == 1 else 1
                    user_db.update_user(user_id, is_god_mode=new_status)
                    mode_text = get_text("god_mode_off" if new_status == 0 else "god_mode_on", lang)
                    await update.message.reply_text(
                        get_text("god_mode_msg", lang, mode=mode_text),
                        reply_markup=self.get_main_keyboard(user_id, lang),
                        parse_mode=ParseMode.MARKDOWN
                    )
                
                elif context.user_data.get('state') == 'searching' or (not text.startswith('/') and not text.startswith('⚡')):
                    model_name = text
                    status_msg = await update.message.reply_text(get_text("searching", lang, name=model_name))
                    try:
                        async with MediaFetcher() as fetcher:
                            creators = await fetcher._get_creators_list()
                            matches = smart_search.find_similar(model_name, creators)
                            if not matches:
                                await status_msg.edit_text(get_text("no_media_found", lang, name=model_name))
                                return
                            # Keep callback_data short and safe: do not include creator name (may contain special chars).
                            keyboard = [[InlineKeyboardButton(m['name'], callback_data=f"sel:{m['service']}:{m['id']}")] for m in matches[:8]]
                            await status_msg.edit_text(get_text("select_model", lang), reply_markup=InlineKeyboardMarkup(keyboard))
                            context.user_data['state'] = None
                    except:
                        await status_msg.edit_text(get_text("error_occurred", lang, error="Timeout"))

            async def show_payment_popup(self, update: Update, user_id: int, lang: str, is_downsell: bool = False):
                pricing = user_db.get_pricing(lang)
                title = get_text("downsell_title" if is_downsell else "vip_offer_title", lang)
                copy = get_text("downsell_copy" if is_downsell else "vip_offer_copy", lang)
                
                if is_downsell:
                    keyboard = [[InlineKeyboardButton(f"⚡ {get_text('btn_vip', lang)} - {pricing['weekly']['label']}", callback_data="buy:weekly_ds")]]
                else:
                    keyboard = [
                        [InlineKeyboardButton(f"💎 {get_text('btn_vip', lang)} (Lifetime) - {pricing['lifetime']['label']}", callback_data="buy:lifetime")],
                        [InlineKeyboardButton(f"📅 {get_text('btn_vip', lang)} (Monthly) - {pricing['monthly']['label']}", callback_data="buy:monthly")],
                        [InlineKeyboardButton(f"⏳ {get_text('btn_vip', lang)} (Weekly) - {pricing['weekly']['label']}", callback_data="buy:weekly")]
                    ]
                
                msg = update.effective_message
                await msg.reply_text(f"{title}\n\n{copy}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

            async def on_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                query = update.callback_query
                await query.answer()
                user_id = update.effective_user.id
                data = query.data
                u_data = user_db.get_user(user_id)
                lang = u_data.get('language', 'pt')

                if data.startswith("setlang:"):
                    new_lang = data.split(":")[1]
                    user_db.update_user(user_id, language=new_lang)
                    try:
                        await query.message.delete()
                    except: pass
                    await self.cmd_start(update, context)

                elif data.startswith("sel:"):
                    # New format: sel:<service>:<creator_id>
                    # Legacy format: sel:<service>:<creator_id>:<name>
                    parts = data.split(":")
                    service = parts[1] if len(parts) > 1 else ""
                    c_id = parts[2] if len(parts) > 2 else ""
                    name = parts[3] if len(parts) > 3 else ""

                    async with MediaFetcher() as fetcher:
                        if not name:
                            # Resolve creator name from the creators list (avoids callback_data length issues)
                            try:
                                creators = await fetcher._get_creators_list()
                                for c in creators:
                                    if str(c.get("id")) == str(c_id) and str(c.get("service")) == str(service):
                                        name = c.get("name") or name
                                        break
                            except Exception:
                                pass
                        if not hasattr(self, "_creator_sessions"):
                            self._creator_sessions = {}
                        self._creator_sessions[user_id] = {"service": service, "c_id": c_id, "name": name}

                        await self.safe_edit_or_send(
                            query,
                            f"🔄 {get_text('loading', lang)} **{self._esc_md(name)}**...",
                            parse_mode=ParseMode.MARKDOWN,
                        )

                        creator = {"service": service, "id": c_id, "name": name}
                        page = await fetcher.fetch_posts_page(creator, offset=0)
                        items = page.get("media_items", [])
                        if not items:
                            await self.safe_edit_or_send(query, get_text("nothing_found", lang))
                            return

                        has_access = user_db.is_license_active(user_id)
                        used_credit = False

                        if not has_access and int(u_data.get('credits', 0)) > 0:
                            user_db.use_credit(user_id)
                            has_access = True
                            used_credit = True

                        if has_access:
                            if used_credit:
                                await query.message.reply_text(get_text("using_credit", lang), parse_mode=ParseMode.MARKDOWN)

                            text = get_text("model_found", lang, name=self._esc_md(name))
                            kb = [
                                [InlineKeyboardButton(get_text("btn_download_all", lang), callback_data=f"dlall:{service}:{c_id}")],
                                [InlineKeyboardButton(get_text("btn_view_page", lang), callback_data=f"dlpage:{service}:{c_id}:0")],
                            ]
                            await self.safe_edit_or_send(
                                query,
                                text,
                                reply_markup=InlineKeyboardMarkup(kb),
                                parse_mode=ParseMode.MARKDOWN,
                            )
                        else:
                            if not user_db.check_preview_limit(user_id):
                                await self.show_payment_popup(update, user_id, lang)
                                return
                            user_db.increment_previews(user_id)
                            await self.safe_edit_or_send(query, get_text("sending_previews", lang, name=name))
                            for item in items[:3]:
                                if await fetcher.download_media(item):
                                    ok = await self.uploader.upload_and_cleanup(item, user_id, caption=f"🔥 Preview: {name}")
                                    if ok:
                                        await asyncio.sleep(1.2)
                            await self.show_payment_popup(update, user_id, lang)

                elif data.startswith("dlall:") or data.startswith("dlpage:") or data.startswith("dlnext:") or data.startswith("dlstop"):
                    # Download pagination flow.
                    # New formats (no name in callback_data to avoid special chars/length):
                    #   dlall:<service>:<creator_id>
                    #   dlpage:<service>:<creator_id>:<offset>
                    #   dlnext:<service>:<creator_id>:<offset>
                    #   dlstop:<service>:<creator_id>
                    # Legacy formats with :<name> are still accepted.

                    parts = data.split(":")
                    action = parts[0]
                    service = parts[1] if len(parts) > 1 else ""
                    c_id = parts[2] if len(parts) > 2 else ""

                    # Resolve creator name from session if possible
                    name = ""
                    if hasattr(self, "_creator_sessions") and user_id in self._creator_sessions:
                        sess = self._creator_sessions[user_id]
                        if str(sess.get("c_id")) == str(c_id) and str(sess.get("service")) == str(service):
                            name = sess.get("name") or ""

                    # Legacy name position
                    if not name and len(parts) > 3 and action in ("dlall", "dlpage", "dlnext", "dlstop"):
                        # dlpage/dlnext legacy: action:service:c_id:name:offset
                        # dlall legacy: action:service:c_id:name
                        if action in ("dlpage", "dlnext") and len(parts) >= 5:
                            name = parts[3]
                        elif action in ("dlall", "dlstop") and len(parts) >= 4:
                            name = parts[3]

                    # Parse offset
                    offset = 0
                    if action in ("dlpage", "dlnext"):
                        try:
                            offset = int(parts[-1])
                        except Exception:
                            offset = 0

                    if action.startswith("dlstop"):
                        try:
                            if hasattr(self, "_dl_sessions"):
                                self._dl_sessions.pop(user_id, None)
                        except Exception:
                            pass
                        await query.answer("✅ Parado.", show_alert=False)
                        await self.safe_edit_or_send(query, "⛔ Download interrompido.", parse_mode=ParseMode.MARKDOWN)
                        return

                    # Session continuation: for dlnext prefer stored offset (prevents wrong offsets)
                    if action == "dlnext" and hasattr(self, "_dl_sessions") and user_id in self._dl_sessions:
                        try:
                            offset = int(self._dl_sessions[user_id].get("offset", offset))
                        except Exception:
                            pass

                    if not hasattr(self, "_dl_sessions"):
                        self._dl_sessions = {}
                    if action == "dlall":
                        offset = 0

                    self._dl_sessions[user_id] = {"service": service, "c_id": c_id, "name": name, "offset": offset}

                    await self.safe_edit_or_send(
                        query,
                        get_text("downloading", lang, name=self._esc_md(name)),
                        parse_mode=ParseMode.MARKDOWN,
                    )

                    # Limit media per page to avoid flooding, but compute next_offset from POSTS count.
                    PAGE_MEDIA_LIMIT = int(os.getenv("PAGE_MEDIA_LIMIT", "120"))

                    async with MediaFetcher() as fetcher:
                        creator = {"service": service, "id": c_id, "name": name}
                        page = await fetcher.fetch_posts_page(creator, offset=offset)
                        posts = page.get("posts", [])
                        items_all = page.get("media_items", [])

                        posts_count = len(posts) if isinstance(posts, list) else 0
                        if posts_count == 0 or not items_all:
                            await self.safe_edit_or_send(
                                query,
                                f"✅ Download completo: **{self._esc_md(name)}**\n\nNão há mais páginas.",
                                parse_mode=ParseMode.MARKDOWN,
                            )
                            try:
                                self._dl_sessions.pop(user_id, None)
                            except Exception:
                                pass
                            return

                        items = items_all[:PAGE_MEDIA_LIMIT]

                        # Per-page transfer stats
                        sent_any = False
                        sent = 0
                        skipped_empty = 0
                        skipped_large = 0
                        errors = 0

                        for i in range(0, len(items), 10):
                            batch = items[i:i+10]
                            for item in batch:
                                try:
                                    if await fetcher.download_media(item):
                                        before = (self.uploader.stats.sent, self.uploader.stats.skipped_empty, self.uploader.stats.skipped_large, self.uploader.stats.errors)
                                        ok = await self.uploader.upload_and_cleanup(item, user_id, caption=f"✅ {name} - VIP")
                                        after = (self.uploader.stats.sent, self.uploader.stats.skipped_empty, self.uploader.stats.skipped_large, self.uploader.stats.errors)
                                        sent += max(0, after[0] - before[0])
                                        skipped_empty += max(0, after[1] - before[1])
                                        skipped_large += max(0, after[2] - before[2])
                                        errors += max(0, after[3] - before[3])
                                        if ok:
                                            sent_any = True
                                            await asyncio.sleep(0.6)
                                    else:
                                        # download failed; skip quickly
                                        continue
                                except Exception as e:
                                    errors += 1
                                    logger.warning(f"Upload loop error: {e}")
                            if sent_any:
                                await asyncio.sleep(1.0)

                        next_offset = offset + max(1, posts_count)
                        self._dl_sessions[user_id]["offset"] = next_offset

                        logger.info(
                            "Page done user=%s creator=%s posts=%s media=%s sent=%s skipped_empty=%s skipped_large=%s errors=%s",
                            user_id,
                            c_id,
                            posts_count,
                            len(items_all),
                            sent,
                            skipped_empty,
                            skipped_large,
                            errors,
                        )

                        kb = [
                            [InlineKeyboardButton("▶️ Baixar próxima página", callback_data=f"dlnext:{service}:{c_id}:{next_offset}")],
                            [InlineKeyboardButton("⛔ Parar", callback_data=f"dlstop:{service}:{c_id}")],
                        ]

                        await self.safe_edit_or_send(
                            query,
                            f"✅ Página concluída: **{self._esc_md(name)}**\n\nEnviados: {sent}\nPulados (vazio): {skipped_empty}\nPulados (grande): {skipped_large}\nErros: {errors}\n\nQuer continuar?",
                            reply_markup=InlineKeyboardMarkup(kb),
                            parse_mode=ParseMode.MARKDOWN,
                        )

                elif data.startswith("asaas_confirm:"):
                    # A2 flow: prompt the user to paste the Asaas payment id after paying via link.
                    try:
                        _, plan = data.split(":", 1)
                    except ValueError:
                        await query.answer()
                        return

                    pricing = user_db.get_pricing(lang).get(plan, {})
                    expected_amount = float(pricing.get("price") or 0.0)

                    context.user_data["state"] = "awaiting_asaas_payment_id"
                    context.user_data["asaas_expected_plan"] = plan
                    context.user_data["asaas_expected_amount"] = expected_amount

                    await self.safe_edit_or_send(
                        query,
                        get_text("payment_prompt_asaas_id", lang),
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    await query.answer()



                elif data.startswith("checkpay:"):
                    # Manual status check (useful when PUBLIC_URL/webhook is not configured)
                    _, provider, external_id = data.split(":", 2)
                    try:
                        if user_db.is_payment_already_paid(provider, external_id):
                            await self.safe_edit(query, get_text("payment_confirmed", lang))
                            return

                        paid = False
                        raw = None
                        if provider == "asaas":
                            client = AsaasClient()
                            status = client.get_payment_status(external_id).upper()
                            raw = {"status": status}
                            paid = status in ("RECEIVED", "CONFIRMED", "RECEIVED_IN_CASH")
                        elif provider == "nowpayments":
                            client = NowPaymentsClient()
                            raw = client.get_payment(external_id)
                            status = str(raw.get("payment_status") or raw.get("paymentstatus") or "").lower()
                            paid = NowPaymentsClient.is_paid_status(status)
                        else:
                            await query.answer()
                            return

                        if paid:
                            rec = user_db.get_payment_by_external_id(provider, external_id)
                            if rec:
                                user_db.mark_payment_paid(provider, external_id, raw_payload=str(raw))
                                user_db.activate_license(int(rec["user_id"]), rec["plan_type"])
                            await self.safe_edit(query, get_text("payment_confirmed", lang))
                        else:
                            await self.safe_edit(query, get_text("payment_pending", lang))

                    except Exception:
                        logger.exception("Payment status check failed")
                        await self.safe_edit(query, get_text("payment_check_failed", lang))
                elif data.startswith("buy:"):
                    # Step 1: user picked a plan -> now let them choose payment method.
                    plan_raw = data.split(":", 1)[1]

                    methods: list[list[InlineKeyboardButton]] = []
                    # Stripe is offered only for EN/ES (international)
                    if lang in ("en", "es") and stripe_available():
                        methods.append([InlineKeyboardButton(get_text("btn_pay_stripe", lang), callback_data=f"paym:{plan_raw}:stripe")])
                    # PIX (Brazil) is offered only for PT (or when currency is BRL) and only if configured
                    if lang == "pt" and asaas_available():
                        methods.append([InlineKeyboardButton(get_text("btn_pay_pix", lang), callback_data=f"paym:{plan_raw}:asaas")])
                    # Crypto can be offered in any language if configured
                    if nowpayments_available() and nowpayments_allowed_for_plan(plan_raw):
                        methods.append([InlineKeyboardButton(get_text("btn_pay_crypto", lang), callback_data=f"paym:{plan_raw}:nowpayments")])

                    if not methods:
                        await self.safe_edit_or_send(
                            query,
                            get_text("payment_no_methods", lang),
                            parse_mode=ParseMode.MARKDOWN,
                        )
                        return

                    await self.safe_edit_or_send(
                        query,
                        get_text("payment_choose_method", lang),
                        reply_markup=InlineKeyboardMarkup(methods),
                        parse_mode=ParseMode.MARKDOWN,
                    )

                elif data.startswith("paym:"):
                    # Step 2: user chose the payment provider for a given plan.
                    try:
                        _, plan_raw, provider = data.split(":", 2)
                    except ValueError:
                        await query.answer()
                        return

                    plan = plan_raw.replace("_ds", "")

                    # If crypto is configured but disabled for this plan (e.g., weekly), block it safely.
                    if provider == "nowpayments" and (not nowpayments_allowed_for_plan(plan_raw)):
                        await self.safe_edit_or_send(
                            query,
                            get_text("crypto_unavailable_plan", lang),
                            parse_mode=ParseMode.MARKDOWN,
                        )
                        return


                    # A2 PIX flow (Asaas Payment Link + manual confirmation):
                    # Do NOT create PIX charges via Asaas API (CPF/CNPJ is required for customers).
                    if provider == "asaas":
                        link_map = {
                            "weekly": (os.getenv("ASAAS_PIX_LINK_WEEKLY") or "").strip(),
                            "monthly": (os.getenv("ASAAS_PIX_LINK_MONTHLY") or "").strip(),
                            "lifetime": (os.getenv("ASAAS_PIX_LINK_LIFETIME") or "").strip(),
                        }
                        pay_link = link_map.get(plan, "")
                        if not pay_link:
                            await self.safe_edit_or_send(
                                query,
                                get_text("payment_no_methods", lang),
                                parse_mode=ParseMode.MARKDOWN,
                            )
                            return
                        await self.safe_edit_or_send(
                            query,
                            get_text("payment_created_pix_link", lang),
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton(get_text("btn_open_payment_link", lang), url=pay_link)],
                                [InlineKeyboardButton(get_text("btn_confirm_payment", lang), callback_data=f"asaas_confirm:{plan}")],
                            ]),
                            parse_mode=ParseMode.MARKDOWN,
                        )
                        return
                    pricing = user_db.get_pricing(lang)[plan]
                    price = pricing['price'] * 0.7 if "_ds" in plan_raw else pricing['price']
                    currency = pricing['currency']
                    base_url = os.getenv("PUBLIC_URL") or os.getenv("RAILWAY_PUBLIC_URL") or ""

                    try:
                        # Explicit payment method creation.
                        payment = create_payment_explicit(
                            provider=provider,
                            user_id=user_id,
                            plan=plan,
                            lang=lang,
                            amount=price,
                            currency=currency,
                            base_url=base_url,
                        )
                        user_db.create_pending_payment(
                            user_id=user_id,
                            provider=payment.provider,
                            external_id=payment.external_id,
                            amount=payment.amount,
                            currency=payment.currency,
                            plan_type=plan,
                        )

                        if payment.provider == "stripe":
                            if not payment.checkout_url:
                                raise RuntimeError("Stripe did not return a checkout URL")
                            await self.safe_edit_or_send(
                                query,
                                get_text("payment_created_stripe", lang),
                                reply_markup=InlineKeyboardMarkup(
                                    [[InlineKeyboardButton(get_text("btn_pay_stripe", lang), url=payment.checkout_url)]]
                                ),
                                parse_mode=ParseMode.MARKDOWN,
                            )
                        elif payment.provider == "nowpayments":
                            details_lines = [get_text("payment_created_crypto", lang)]
                            if payment.checkout_url:
                                details_lines.append(payment.checkout_url)
                            if getattr(payment, "crypto_pay_address", None):
                                details_lines.append(f"**Address:** `{payment.crypto_pay_address}`")
                            if getattr(payment, "crypto_pay_amount", None) and getattr(payment, "crypto_pay_currency", None):
                                details_lines.append(f"**Amount:** `{payment.crypto_pay_amount} {payment.crypto_pay_currency}`")
                            msg = "\n".join(details_lines)
                            kb = InlineKeyboardMarkup(
                                [[InlineKeyboardButton(get_text("btn_check_payment", lang), callback_data=f"checkpay:nowpayments:{payment.external_id}")]]
                            )
                            await self.safe_edit_or_send(query, msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
                        else:
                            # PIX (Asaas) - Payment Link (A2)
                            link = payment.checkout_url or ""
                            msg = get_text("payment_created_pix_link", lang)
                            kb = InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton(get_text("btn_open_payment_link", lang), url=link)],
                                    [InlineKeyboardButton(get_text("btn_confirm_payment", lang), callback_data=f"asaas_confirm:{plan}")],
                                ]
                            )
                            await self.safe_edit_or_send(query, msg, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

                    except Exception as e:
                        # Special-case only the Stripe method-unavailable error.
                        if (provider == "stripe") and is_stripe_no_payment_methods_error(e):
                            # If crypto is configured, offer it as an option; otherwise show a friendly message.
                            if nowpayments_available() and nowpayments_allowed_for_plan(plan_raw):
                                kb = InlineKeyboardMarkup(
                                    [[InlineKeyboardButton(get_text("btn_pay_crypto", lang), callback_data=f"paym:{plan_raw}:nowpayments")]]
                                )
                                await self.safe_edit_or_send(
                                    query,
                                    get_text("stripe_unavailable", lang),
                                    reply_markup=kb,
                                    parse_mode=ParseMode.MARKDOWN,
                                )
                                return
                            await self.safe_edit_or_send(query, get_text("stripe_unavailable", lang), parse_mode=ParseMode.MARKDOWN)
                            return

                        # If user selected PIX but Asaas isn't configured, give a clear message and optionally offer crypto.
                        if (provider in ("asaas", "pix")) and ("ASAAS_ACCESS_TOKEN is not set" in str(e)):
                            if nowpayments_available() and nowpayments_allowed_for_plan(plan_raw):
                                kb = InlineKeyboardMarkup(
                                    [[InlineKeyboardButton(get_text("btn_pay_crypto", lang), callback_data=f"paym:{plan_raw}:nowpayments")]]
                                )
                                await self.safe_edit_or_send(
                                    query,
                                    get_text("pix_unavailable", lang),
                                    reply_markup=kb,
                                    parse_mode=ParseMode.MARKDOWN,
                                )
                                return
                            await self.safe_edit_or_send(query, get_text("pix_unavailable", lang), parse_mode=ParseMode.MARKDOWN)
                            return

                        logger.exception("Payment creation failed")
                        await self.safe_edit(query, get_text("payment_error", lang) + f"\n\n{e}")


        # ----------------------------
        # Embedded Webhook HTTP server
        # ----------------------------
        async def start_webhook_server(tg_bot):
            """
            Starts an aiohttp server to receive payment webhooks.
            Railway-friendly: listens on $PORT.
            """
            port = int(os.getenv("PORT", "8080"))
            host = "0.0.0.0"

            async def healthz(_request):
                return web.json_response({"ok": True})

            async def stripe_success(_request):
                return web.Response(text="OK. You can return to Telegram.")

            async def stripe_cancel(_request):
                return web.Response(text="Payment canceled. You can return to Telegram.")

            async def stripe_webhook(request):
                payload = await request.read()
                sig_header = request.headers.get("Stripe-Signature", "")
                endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

                if not endpoint_secret:
                    return web.Response(status=500, text="STRIPE_WEBHOOK_SECRET not configured")

                try:
                    import stripe  # type: ignore
                    event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
                except Exception as e:
                    logger.warning(f"Stripe webhook signature/parse error: {e}")
                    return web.Response(status=400, text="Invalid payload")

                if event.get("type") == "checkout.session.completed":
                    session = event["data"]["object"]
                    external_id = session.get("id")
                    metadata = session.get("metadata") or {}
                    # Try DB mapping first (preferred), then metadata fallback.
                    rec = user_db.get_payment_by_external_id("stripe", str(external_id)) if external_id else None
                    if rec and rec.get("status") == "paid":
                        return web.Response(text="Already processed")
                    try:
                        if rec:
                            user_id_ = int(rec["user_id"])
                            plan_type = rec["plan_type"]
                            user_db.mark_payment_paid("stripe", str(external_id), raw_payload=str(session))
                            user_db.activate_license(user_id_, plan_type)
                            lang_ = user_db.get_user(user_id_).get("language", "pt")
                            await tg_bot.send_message(chat_id=user_id_, text=get_text("payment_confirmed", lang_))
                        else:
                            # fallback: metadata
                            user_id_ = int(metadata.get("user_id", "0"))
                            plan_type = metadata.get("plan", "monthly")
                            if user_id_:
                                user_db.create_pending_payment(
                                    user_id=user_id_,
                                    provider="stripe",
                                    external_id=str(external_id),
                                    amount=float(session.get("amount_total", 0)) / 100.0,
                                    currency=(session.get("currency") or "usd").upper(),
                                    plan_type=plan_type,
                                    raw_payload=str(session),
                                )
                                user_db.mark_payment_paid("stripe", str(external_id), raw_payload=str(session))
                                user_db.activate_license(user_id_, plan_type)
                                lang_ = user_db.get_user(user_id_).get("language", "pt")
                                await tg_bot.send_message(chat_id=user_id_, text=get_text("payment_confirmed", lang_))
                    except Exception as e:
                        logger.exception(f"Stripe webhook processing error: {e}")
                        return web.Response(status=500, text="Processing error")

                return web.Response(text="OK")

            async def asaas_webhook(request):
                # Optional token check (recommended). Supports query token or header token.
                try:
                    client = AsaasClient()
                except Exception as e:
                    logger.exception(f"Asaas client init failed: {e}")
                    return web.Response(status=500, text="Asaas not configured")

                if not client.webhook_is_valid({k.lower(): v for k, v in request.headers.items()}, dict(request.query)):
                    return web.Response(status=401, text="Unauthorized")

                try:
                    data = await request.json()
                except Exception:
                    return web.Response(status=400, text="Invalid JSON")

                event = str(data.get("event") or "")
                payment_obj = data.get("payment") or {}
                external_id = str(payment_obj.get("id") or data.get("paymentId") or "")

                if event in ("PAYMENT_RECEIVED", "PAYMENT_CONFIRMED", "PAYMENT_RECEIVED_IN_CASH"):
                    try:
                        rec = user_db.get_payment_by_external_id("asaas", external_id)
                        if rec:
                            user_id_ = int(rec["user_id"])
                            plan_type = rec["plan_type"]
                            user_db.mark_payment_paid("asaas", external_id, raw_payload=str(data))
                            user_db.activate_license(user_id_, plan_type)
                            lang_ = user_db.get_user(user_id_).get("language", "pt")
                            await tg_bot.send_message(chat_id=user_id_, text=get_text("payment_confirmed", lang_))
                    except Exception as e:
                        logger.exception(f"Asaas webhook processing error: {e}")
                        return web.Response(status=500, text="Processing error")

                return web.Response(text="OK")

            async def nowpayments_webhook(request):
                # Validate IPN signature (HMAC SHA-512) using NOWPAYMENTS_IPN_SECRET
                try:
                    client = NowPaymentsClient()
                except Exception as e:
                    logger.exception(f"NOWPayments client init failed: {e}")
                    return web.Response(status=500, text="NOWPayments not configured")

                try:
                    data = await request.json()
                except Exception:
                    return web.Response(status=400, text="Invalid JSON")

                sig = request.headers.get("x-nowpayments-sig") or request.headers.get("X-NOWPAYMENTS-SIG") or ""
                if not client.verify_ipn(data, sig):
                    return web.Response(status=401, text="Invalid signature")

                payment_id = str(data.get("payment_id") or "")
                status = str(data.get("payment_status") or "").lower()

                if payment_id and NowPaymentsClient.is_paid_status(status):
                    try:
                        rec = user_db.get_payment_by_external_id("nowpayments", payment_id)
                        if rec:
                            user_id_ = int(rec["user_id"])
                            plan_type = rec["plan_type"]
                            user_db.mark_payment_paid("nowpayments", payment_id, raw_payload=str(data))
                            user_db.activate_license(user_id_, plan_type)
                            lang_ = user_db.get_user(user_id_).get("language", "en")
                            await tg_bot.send_message(chat_id=user_id_, text=get_text("payment_confirmed", lang_))
                    except Exception as e:
                        logger.exception(f"NOWPayments webhook processing error: {e}")
                        return web.Response(status=500, text="Processing error")

                return web.Response(text="OK")

            async def pushinpay_webhook(request):
                # Legacy endpoint kept to avoid stray calls after migration.
                return web.Response(status=410, text="PushinPay disabled (migrated)")
            web_app = web.Application()
            web_app.add_routes(
                [
                    web.get("/healthz", healthz),
                    web.post("/webhooks/stripe", stripe_webhook),
                    web.post("/webhooks/asaas", asaas_webhook),
                    web.post("/webhooks/nowpayments", nowpayments_webhook),
                    web.post("/webhooks/pushinpay", pushinpay_webhook),
                    web.get("/stripe/success", stripe_success),
                    web.get("/stripe/cancel", stripe_cancel),
                ]
            )

            runner = web.AppRunner(web_app)
            await runner.setup()
            site = web.TCPSite(runner, host=host, port=port)
            await site.start()
            logger.info(f"🌐 Webhook server listening on http://{host}:{port}")
            return runner

        # --- Single instance lock (prevents 409 Conflict getUpdates) ---
        lock_path = os.getenv("BOT_LOCK_PATH") or os.path.join(os.getenv("DATA_DIR", "/data"), "bot.lock")
        try:
            os.makedirs(os.path.dirname(lock_path), exist_ok=True)
            _lock_fd = open(lock_path, "w")
            fcntl.flock(_lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.info(f"🔒 Acquired bot lock at: {lock_path}")
        except BlockingIOError:
            logger.error("🚫 Another instance is already running (getUpdates 409 conflict). Exiting.")
            return
        except Exception as e:
            logger.warning(f"Could not acquire bot lock ({e}). Continuing without lock.")
        # --------------------------------------------------------------

        # Initialize Application
        app = Application.builder().token(config.BOT_TOKEN).build()
        uploader = TelegramUploader(app.bot)
        bot_logic = VIPBotUltra(app, uploader)

        # Register Handlers
        app.add_handler(CommandHandler("start", bot_logic.cmd_start))
        app.add_handler(CallbackQueryHandler(bot_logic.on_callback_query))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_logic.handle_message))
        
        async def _on_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
            logger.exception("Unhandled exception", exc_info=context.error)
        app.add_error_handler(_on_error)

        
        logger.info("✅ Bot Handlers registered. Starting polling...")
        await app.initialize()
        await app.start()

        # Start webhook server (for Stripe/PushinPay)
        # Important: start it AFTER Application.initialize()/start() so the Bot's
        # internal HTTP session is ready when we need to send Telegram messages
        # from webhook callbacks.
        try:
            await start_webhook_server(app.bot)
        except Exception as e:
            logger.warning(f"Webhook server failed to start (payments will require manual check): {e}")

        await app.updater.start_polling(drop_pending_updates=True)
        
        stop_event = asyncio.Event()
        await stop_event.wait()

    except Exception as e:
        logger.critical(f"💥 CRITICAL CRASH: {e}", exc_info=True)
        sys.exit(1)