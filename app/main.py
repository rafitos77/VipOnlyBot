
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
import json
import sqlite3
from aiohttp import web

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
        from app.pushinpay_integration import pushinpay_client
        
        # Telegram Libraries
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice
        from telegram.ext import (
            Application,
            CommandHandler,
            ContextTypes,
            CallbackQueryHandler,
            MessageHandler,
            PreCheckoutQueryHandler,
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

            async def get_main_keyboard(self, user_id, lang):
                """Generate the main persistent GUI keyboard (async to avoid blocking DB)."""
                is_admin = (user_id == config.ADMIN_ID)
                u_data = await user_db.async_get_user(user_id)
                
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
                u_data = await user_db.async_get_user(user.id)
                msg = update.effective_message
                
                # Handle Referral
                if context.args and context.args[0].startswith('ref'):
                    try:
                        referrer_id = int(context.args[0].replace('ref', ''))
                        if referrer_id != user.id:
                            await user_db.async_process_referral(user.id, referrer_id)
                            try:
                                ref_data = await user_db.async_get_user(referrer_id)
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
                                            keyboard = await self.get_main_keyboard(user.id, lang)
                                            await self.uploader.upload_and_cleanup(
                                                pick, user.id, 
                                                caption=f"{welcome_title}\n\n{welcome_copy}",
                                                reply_markup=keyboard
                                            )
                                            return
                    except Exception as e:
                        logger.error(f"Visual welcome failed: {e}")
                    
                    # Fallback to text only
                    try:
                        keyboard = await self.get_main_keyboard(user.id, lang)
                        await status_msg.edit_text(
                            f"{welcome_title}\n\n{welcome_copy}",
                            reply_markup=keyboard,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        keyboard = await self.get_main_keyboard(user.id, lang)
                        await msg.reply_text(
                            f"{welcome_title}\n\n{welcome_copy}",
                            reply_markup=keyboard,
                            parse_mode=ParseMode.MARKDOWN
                        )

            async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                user_id = update.effective_user.id
                text = update.message.text
                if not text: return
                
                u_data = await user_db.async_get_user(user_id)
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
                    is_vip = "✅ VIP" if await user_db.async_is_license_active(user_id) else "❌ FREE"
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
                    await user_db.async_update_user(user_id, is_god_mode=new_status)
                    mode_text = get_text("god_mode_off" if new_status == 0 else "god_mode_on", lang)
                    keyboard = await self.get_main_keyboard(user_id, lang)
                    await update.message.reply_text(
                        get_text("god_mode_msg", lang, mode=mode_text),
                        reply_markup=keyboard,
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
                
                # Same plan buttons; downsell uses 30% discount applied at buy: step
                keyboard = [
                    [InlineKeyboardButton(f"💎 {get_text('btn_vip', lang)} (Lifetime) - {pricing['lifetime']['label']}", callback_data="buy:lifetime_ds" if is_downsell else "buy:lifetime")],
                    [InlineKeyboardButton(f"📅 {get_text('btn_vip', lang)} (Monthly) - {pricing['monthly']['label']}", callback_data="buy:monthly_ds" if is_downsell else "buy:monthly")],
                    [InlineKeyboardButton(f"⏳ {get_text('btn_vip', lang)} (Weekly) - {pricing['weekly']['label']}", callback_data="buy:weekly_ds" if is_downsell else "buy:weekly")]
                ]
                
                msg = update.effective_message
                await msg.reply_text(f"{title}\n\n{copy}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

            async def on_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                query = update.callback_query
                await query.answer()
                user_id = update.effective_user.id
                data = query.data
                u_data = await user_db.async_get_user(user_id)
                lang = u_data.get('language', 'pt')

                if data.startswith("setlang:"):
                    new_lang = data.split(":")[1]
                    await user_db.async_update_user(user_id, language=new_lang)
                    try:
                        await query.message.delete()
                    except: pass
                    await self.cmd_start(update, context)

                elif data.startswith("sel:"):
                    parts = data.split(":", 3)  # sel, service, c_id, name (name may contain colons)
                    if len(parts) < 4:
                        await query.answer(get_text("error_occurred", lang, error="Invalid data"))
                        return
                    _, service, c_id, name = parts[0], parts[1], parts[2], parts[3]
                    await query.edit_message_text(f"🔄 {get_text('loading', lang)} **{name}**...")
                    
                    async with MediaFetcher() as fetcher:
                        creator = {'service': service, 'id': c_id, 'name': name}
                        items = await fetcher.fetch_posts_paged(creator, offset=0)
                        if not items:
                            await query.edit_message_text(get_text("nothing_found", lang))
                            return
                        
                        has_access = await user_db.async_is_license_active(user_id)
                        used_credit = False
                        
                        if not has_access and int(u_data.get('credits', 0)) > 0:
                            await user_db.async_use_credit(user_id)
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
                            if not await user_db.async_check_preview_limit(user_id):
                                await self.show_payment_popup(update, user_id, lang)
                                return
                            await user_db.async_increment_previews(user_id)
                            await query.edit_message_text(get_text("sending_previews", lang, name=name))
                            for item in items[:3]:
                                if await fetcher.download_media(item):
                                    await self.uploader.upload_and_cleanup(item, user_id, caption=f"🔥 Preview: {name}")
                                    await asyncio.sleep(1.5)
                            await self.show_payment_popup(update, user_id, lang)

                elif data.startswith("dlall:") or data.startswith("dlpage:"):
                    parts = data.split(":", 4)  # max 5 parts: action, service, c_id, [offset], name
                    action = parts[0]
                    service, c_id = parts[1], parts[2]
                    if action == "dlpage" and len(parts) >= 5:
                        offset = int(parts[3])
                        name = parts[4]  # name may contain colons
                    else:
                        offset = 0
                        name = ":".join(parts[3:]) if len(parts) > 3 else ""  # name may contain colons
                    
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
                    
                    # Store plan type for successful payment callback
                    context.user_data['pending_plan_type'] = plan
                    
                    # For international users (USD), use Telegram Native Payments (Stripe)
                    if pricing['currency'] == 'USD':
                        if not config.STRIPE_API_TOKEN:
                            await query.edit_message_text(get_text("payment_error", lang) + "\n\n⚠️ Stripe is not configured.")
                            return
                        
                        title = get_text("stripe_invoice_title", lang)
                        description = get_text("stripe_invoice_description", lang, label=pricing['label'])
                        # Persist a pending Stripe transaction before sending invoice so state is recoverable
                        temp_txid = f"stripe_{user_id}_{int(datetime.now().timestamp())}"
                        await user_db.async_add_transaction(
                            user_id=user_id,
                            transaction_id=temp_txid,
                            gateway="Stripe (Telegram Payments)",
                            amount=price,
                            currency=currency,
                            plan_type=plan,
                            status="PENDING",
                            status_detail=None
                        )
                        # Include plan_type and temp txid in payload
                        payload = f"VIP_{plan}_{user_id}_{temp_txid}"
                        provider_token = config.STRIPE_API_TOKEN
                        currency = pricing['currency']
                        price_amount = int(price * 100) # Telegram uses cents

                        await context.bot.send_invoice(
                            chat_id=user_id,
                            title=title,
                            description=description,
                            payload=payload,
                            provider_token=provider_token,
                            currency=currency,
                            prices=[LabeledPrice(label=pricing['label'], amount=price_amount)],
                            need_name=False,
                            need_phone_number=False,
                            need_email=False,
                            is_flexible=False,
                            disable_notification=False,
                            protect_content=False,
                            reply_to_message_id=None,
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text("btn_pay_stripe", lang), pay=True)]])
                        )
                    elif pricing['currency'] == 'BRL':
                        if not config.PUSHINPAY_API_KEY or not config.WEBHOOK_URL:
                            await query.edit_message_text(get_text("payment_error", lang) + "\n\n⚠️ Pushin Pay is not configured.")
                            return
                        
                        title = get_text("pix_invoice_title", lang)
                        description = get_text("pix_invoice_description", lang, label=pricing['label'])
                        reference_id = f"user_{user_id}_plan_{plan}_{datetime.now().timestamp()}"
                        webhook_url = f"{config.WEBHOOK_URL}/pushinpay_webhook"

                        # Persist pending transaction using reference_id as temporary transaction id.
                        # This ensures we can recover state after restarts. We'll attempt to update
                        # the transaction_id to the provider id once the charge is created.
                        await user_db.async_add_transaction(
                            user_id=user_id,
                            transaction_id=reference_id,
                            gateway="Pushin Pay (Pix)",
                            amount=price,
                            currency="BRL",
                            plan_type=plan,
                            status="PENDING",
                            status_detail=None
                        )

                        # Create the Pix charge asynchronously (non-blocking)
                        pix_charge = await pushinpay_client.create_pix_charge(price, reference_id, webhook_url)
                        if pix_charge and pix_charge.get("status") == "pending":
                            qr_code_image = pix_charge.get("qr_code_image")
                            qr_code_text = pix_charge.get("qr_code_text")
                            provider_id = pix_charge.get("id")

                            # Update the transaction record to use the provider transaction id
                            if provider_id:
                                updated = await user_db.async_update_transaction_id(reference_id, provider_id)
                                if not updated:
                                    logger.warning(f"Could not update local transaction id {reference_id} -> {provider_id}")

                            await query.edit_message_text(
                                get_text("pix_order_created", lang, label=pricing['label']),
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(get_text("btn_pix_confirm", lang), callback_data=f"check_pix:{provider_id or reference_id}")]]),
                                parse_mode=ParseMode.MARKDOWN
                            )

                            # Send QR image (if provided) and code as caption
                            if qr_code_image:
                                await context.bot.send_photo(
                                    chat_id=user_id,
                                    photo=qr_code_image,
                                    caption=f"`{qr_code_text}`\n\n{get_text('pix_scan_qr', lang)}",
                                    parse_mode=ParseMode.MARKDOWN
                                )
                            else:
                                # Fallback: send the QR code text only
                                await context.bot.send_message(chat_id=user_id, text=f"`{qr_code_text}`\n\n{get_text('pix_scan_qr', lang)}", parse_mode=ParseMode.MARKDOWN)
                        else:
                            await query.edit_message_text(get_text("payment_error_pix", lang))
                    else:
                        await query.edit_message_text(get_text("payment_error_unsupported_currency", lang))

                elif data.startswith("check_pix:"):
                    # Manual check for Pix payment status
                    transaction_id = data.split(":")[1]
                    await query.answer(get_text("checking_payment", lang))
                    
                        # Check transaction status in database (async)
                    trans = await user_db.async_get_transaction(transaction_id)
                    if trans:
                        if trans.get('status') == 'PAID':
                            plan_type = trans.get('plan_type')
                            if await user_db.async_is_license_active(user_id):
                                await query.edit_message_text(get_text("payment_success", lang))
                            else:
                                await user_db.async_activate_license(user_id, plan_type)
                                await query.edit_message_text(get_text("payment_success", lang))
                        elif trans.get('status') == 'PENDING':
                            try:
                                charge_data = await pushinpay_client.get_charge_status(transaction_id)

                                if charge_data:
                                    if charge_data.get('status') == 'paid':
                                        await user_db.async_update_transaction_status(transaction_id, 'PAID', 'Payment confirmed via API')
                                        plan_type = trans.get('plan_type')
                                        if await user_db.async_is_license_active(user_id):
                                            await query.edit_message_text(get_text("payment_success", lang))
                                        else:
                                            await user_db.async_activate_license(user_id, plan_type)
                                            await query.edit_message_text(get_text("payment_success", lang))
                                    else:
                                        await query.answer(get_text("payment_still_pending", lang), show_alert=True)
                                else:
                                    await query.answer(get_text("payment_check_error", lang), show_alert=True)
                            except Exception as e:
                                logger.error(f"Error checking Pix payment: {e}")
                                await query.answer(get_text("payment_check_error", lang), show_alert=True)
                        else:
                            await query.answer(get_text("payment_not_found", lang), show_alert=True)
                    else:
                        await query.answer(get_text("payment_not_found", lang), show_alert=True)

            async def pre_checkout_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Handle Stripe pre-checkout query (Telegram Native Payments)"""
                query = update.pre_checkout_query
                user_id = query.from_user.id
                u_data = await user_db.async_get_user(user_id)
                lang = u_data.get('language', 'pt')
                
                # Always approve the checkout query
                # Telegram will handle the actual payment processing
                await query.answer(ok=True)
                logger.info(f"Pre-checkout approved for user {user_id}")

            async def successful_payment_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Handle successful Stripe payment (Telegram Native Payments)"""
                message = update.message
                user_id = message.from_user.id
                payment = message.successful_payment
                u_data = await user_db.async_get_user(user_id)
                lang = u_data.get('language', 'pt')
                
                # Get plan type from context (stored when invoice was sent)
                plan_type = context.user_data.get('pending_plan_type')
                
                if not plan_type:
                    # Try to infer from payment amount
                    total_amount = payment.total_amount / 100  # Convert from cents
                    pricing = user_db.get_pricing(lang)
                    
                    # Match amount to plan
                    for plan, plan_data in pricing.items():
                        if abs(plan_data['price'] - total_amount) < 0.01:
                            plan_type = plan
                            break
                    
                    # Also try to extract from payload if available
                    if not plan_type and payment.invoice_payload:
                        payload_parts = payment.invoice_payload.split('_')
                        if len(payload_parts) >= 2 and payload_parts[0] == 'VIP':
                            plan_type = payload_parts[1]
                            logger.info(f"Recovered plan_type {plan_type} from payload")
                
                if plan_type:
                    # Attempt to recover temp transaction id from invoice payload (we store it when sending)
                    payload_txid = None
                    if payment.invoice_payload:
                        parts = payment.invoice_payload.split('_')
                        # payload format: VIP_{plan}_{user_id}_{temp_txid}
                        if len(parts) >= 4 and parts[0] == 'VIP':
                            payload_txid = "_".join(parts[3:])

                    if payload_txid:
                        updated = await user_db.async_update_transaction_id(payload_txid, payment.telegram_payment_charge_id)
                        if updated:
                            # mark as PAID
                            await user_db.async_update_transaction_status(payment.telegram_payment_charge_id, 'PAID', f"Invoice: {payment.invoice_payload}")
                        else:
                            # create new record if update failed
                            await user_db.async_add_transaction(
                                user_id=user_id,
                                transaction_id=payment.telegram_payment_charge_id,
                                gateway="Stripe (Telegram Payments)",
                                amount=payment.total_amount / 100,
                                currency=payment.currency,
                                plan_type=plan_type,
                                status="PAID",
                                status_detail=f"Invoice: {payment.invoice_payload}"
                            )
                    else:
                        # No payload txid recovered, insert transaction record
                        await user_db.async_add_transaction(
                            user_id=user_id,
                            transaction_id=payment.telegram_payment_charge_id,
                            gateway="Stripe (Telegram Payments)",
                            amount=payment.total_amount / 100,
                            currency=payment.currency,
                            plan_type=plan_type,
                            status="PAID",
                            status_detail=f"Invoice: {payment.invoice_payload}"
                        )

                    # Activate license (idempotent - safe to call multiple times)
                    if not await user_db.async_is_license_active(user_id):
                        await user_db.async_activate_license(user_id, plan_type)
                    else:
                        logger.info(f"User {user_id} already has active license, skipping activation")

                    await message.reply_text(
                        get_text("payment_success", lang),
                        parse_mode=ParseMode.MARKDOWN
                    )
                    logger.info(f"License {plan_type} activated for user {user_id} via Stripe")
                else:
                    await message.reply_text(
                        get_text("payment_success_no_plan", lang),
                        parse_mode=ParseMode.MARKDOWN
                    )
                    logger.warning(f"Payment received but plan type not found for user {user_id}")

        # Initialize Application
        app = Application.builder().token(config.BOT_TOKEN).build()
        uploader = TelegramUploader(app.bot)
        bot_logic = VIPBotUltra(app, uploader)

        # Register Handlers
        app.add_handler(CommandHandler("start", bot_logic.cmd_start))
        app.add_handler(CallbackQueryHandler(bot_logic.on_callback_query))
        app.add_handler(PreCheckoutQueryHandler(bot_logic.pre_checkout_query))
        app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, bot_logic.successful_payment_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_logic.handle_message))
        
        logger.info("✅ Bot Handlers registered. Starting polling...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        
        # Start webhook server for Pushin Pay (if WEBHOOK_URL is configured)
        webhook_runner = None
        if config.WEBHOOK_URL:
            try:
                from app.webhook_server import start_webhook_server
                webhook_port = int(os.getenv("WEBHOOK_PORT", "8080"))
                webhook_runner = await start_webhook_server(port=webhook_port)
                logger.info(f"✅ Webhook server started on port {webhook_port}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to start webhook server: {e}")
        
        stop_event = asyncio.Event()
        await stop_event.wait()

    except Exception as e:
        logger.critical(f"💥 CRITICAL CRASH: {e}", exc_info=True)
        sys.exit(1)
