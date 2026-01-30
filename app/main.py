
"""
Main bot module - v8.3 Global Edition
Telegram VIP Media Bot - Forbidden Access Portal
"""

import logging
import asyncio
import os
import sys
import random
from datetime import datetime

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
        from app.paypal_integration import paypal_client
        
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
                            keyboard = [[InlineKeyboardButton(m['name'], callback_data=f"sel:{m['service']}:{m['id']}:{m['name'][:20]}")] for m in matches[:8]]
                            await status_msg.edit_text(get_text("select_model", lang), reply_markup=InlineKeyboardMarkup(keyboard))
                            context.user_data['state'] = None
                    except:
                        await status_msg.edit_text(get_text("error_occurred", lang, error="Timeout"))

            async def show_payment_popup(self, update: Update, user_id: int, lang: str, is_downsell: bool = False):
                pricing = user_db.get_pricing(lang)
                title = get_text("downsell_title" if is_downsell else "vip_offer_title", lang)
                copy = get_text("downsell_copy" if is_downsell else "vip_offer_copy", lang)
                
                if is_downsell:
                    keyboard = [[InlineKeyboardButton(f"⚡ {get_text('btn_pay_paypal', lang)} - {pricing['weekly']['label']}", callback_data="buy:weekly_ds")]]
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
                    _, service, c_id, name = data.split(":")
                    await query.edit_message_text(f"🔄 {get_text('loading', lang)} **{name}**...")
                    
                    async with MediaFetcher() as fetcher:
                        creator = {'service': service, 'id': c_id, 'name': name}
                        items = await fetcher.fetch_posts_paged(creator, offset=0)
                        if not items:
                            await query.edit_message_text(get_text("nothing_found", lang))
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
                            
                            text = get_text("model_found", lang, name=name)
                            kb = [[InlineKeyboardButton(get_text("btn_download_all", lang), callback_data=f"dlall:{service}:{c_id}:{name[:20]}")],
                                  [InlineKeyboardButton(get_text("btn_view_page", lang), callback_data=f"dlpage:{service}:{c_id}:0:{name[:20]}")]]
                            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
                        else:
                            if not user_db.check_preview_limit(user_id):
                                await self.show_payment_popup(update, user_id, lang)
                                return
                            user_db.increment_previews(user_id)
                            await query.edit_message_text(get_text("sending_previews", lang, name=name))
                            for item in items[:3]:
                                if await fetcher.download_media(item):
                                    await self.uploader.upload_and_cleanup(item, user_id, caption=f"🔥 Preview: {name}")
                                    await asyncio.sleep(1.5)
                            await self.show_payment_popup(update, user_id, lang)

                elif data.startswith("dlall:") or data.startswith("dlpage:"):
                    parts = data.split(":")
                    action, service, c_id, name = parts[0], parts[1], parts[2], parts[3]
                    offset = int(parts[4]) if action == "dlpage" else 0
                    
                    await query.edit_message_text(get_text("downloading", lang, name=name))
                    async with MediaFetcher() as fetcher:
                        creator = {'service': service, 'id': c_id, 'name': name}
                        items = await fetcher.fetch_posts_paged(creator, offset=offset)
                        for i in range(0, min(len(items), 50), 10):
                            batch = items[i:i+10]
                            for item in batch:
                                if await fetcher.download_media(item):
                                    await self.uploader.upload_and_cleanup(item, user_id, caption=f"✅ {name} - VIP")
                                    await asyncio.sleep(1.2)
                            await asyncio.sleep(2)
                        await query.message.reply_text(get_text("download_complete", lang))

                elif data.startswith("buy:"):
                    plan_raw = data.split(":")[1]
                    plan = plan_raw.replace("_ds", "")
                    pricing = user_db.get_pricing(lang)[plan]
                    price = pricing['price'] * 0.7 if "_ds" in plan_raw else pricing['price']
                    order = paypal_client.create_order(price, pricing['currency'], "https://t.me/YourBot", "https://t.me/YourBot")
                    if order:
                        link = next(l['href'] for l in order['links'] if l['rel'] == 'approve')
                        await query.edit_message_text(get_text("order_created", lang, label=pricing['label']), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text("btn_pay_paypal", lang), url=link)]]))
                    else:
                        await query.edit_message_text(get_text("payment_error", lang))

        # Initialize Application
        app = Application.builder().token(config.BOT_TOKEN).build()
        uploader = TelegramUploader(app.bot)
        bot_logic = VIPBotUltra(app, uploader)

        # Register Handlers
        app.add_handler(CommandHandler("start", bot_logic.cmd_start))
        app.add_handler(CallbackQueryHandler(bot_logic.on_callback_query))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_logic.handle_message))
        
        logger.info("✅ Bot Handlers registered. Starting polling...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        
        stop_event = asyncio.Event()
        await stop_event.wait()

    except Exception as e:
        logger.critical(f"💥 CRITICAL CRASH: {e}", exc_info=True)
        sys.exit(1)
