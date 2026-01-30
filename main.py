"""
Main bot module - Senior Architecture
Telegram VIP Media Bot - Direct User Delivery
"""

import logging
import asyncio
import os
import sys
from datetime import datetime

# Configure logging early and globally
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add current directory to path to ensure local imports work in any environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

async def run_bot():
    """
    Main entry point for the bot.
    Uses lazy imports to prevent circular dependency crashes and ModuleNotFoundErrors.
    """
    logger.info("🚀 Starting Bot in Senior Mode...")
    
    try:
        # 1. Import Configuration
        from config import Config
        config = Config()
        
        if not config.validate():
            logger.critical("❌ Configuration validation failed. Bot will not start.")
            return

        # 2. Import Telegram Libraries
        from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import (
            Application,
            CommandHandler,
            ContextTypes,
            CallbackQueryHandler,
            MessageHandler,
            filters
        )
        from telegram.constants import ParseMode
        
        # 3. Import Local Modules (Lazy)
        from fetcher import MediaFetcher
        from uploader import TelegramUploader
        from languages import get_text
        from users_db import user_db
        from smart_search import smart_search
        from paypal_integration import paypal_client
        
        logger.info("✅ All modules loaded successfully.")

        class VIPBotPV:
            def __init__(self, app_instance, uploader_instance):
                self.app = app_instance
                self.uploader = uploader_instance

            async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                user = update.effective_user
                u_data = user_db.get_user(user.id)
                lang = u_data.get('language', 'pt')
                
                welcome = {
                    'pt': f"👋 Olá, {user.first_name}!\n\n🤖 **Bot de Mídias VIP**\n\nBusque modelos e receba mídias direto aqui no seu PV.\n\nUse /search <nome> para começar.",
                    'es': f"👋 ¡Hola, {user.first_name}!\n\n🤖 **Bot de Medios VIP**\n\nBusca modelos y recibe medios directamente aquí en tu PV.\n\nUsa /search <nombre> para comenzar.",
                    'en': f"👋 Hello, {user.first_name}!\n\n🤖 **VIP Media Bot**\n\nSearch for models and receive media directly here in your DM.\n\nUse /search <name> to start."
                }
                await update.message.reply_text(welcome.get(lang, welcome['pt']), parse_mode=ParseMode.MARKDOWN)

            async def cmd_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                user_id = update.effective_user.id
                u_data = user_db.get_user(user_id)
                lang = u_data.get('language', 'pt')
                
                if not context.args:
                    await update.message.reply_text(get_text("search_usage", lang))
                    return

                if user_id != config.ADMIN_ID and not user_db.check_preview_limit(user_id):
                    await self.show_payment_popup(update, user_id, lang)
                    return

                model_name = " ".join(context.args)
                status_msg = await update.message.reply_text(f"🔍 {get_text('searching', lang, name=model_name)}")

                try:
                    async with MediaFetcher() as fetcher:
                        creators = await fetcher._get_creators_list()
                        matches = smart_search.find_similar(model_name, creators)
                        
                        if not matches:
                            await status_msg.edit_text(get_text("no_media_found", lang, name=model_name))
                            return

                        keyboard = []
                        for m in matches[:8]:
                            keyboard.append([InlineKeyboardButton(m['name'], callback_data=f"sel:{m['service']}:{m['id']}:{m['name'][:20]}")])
                        
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await status_msg.edit_text("✅ Encontramos modelos similares. Escolha uma:", reply_markup=reply_markup)
                except Exception as e:
                    logger.error(f"Search error: {e}")
                    await status_msg.edit_text("❌ Erro ao realizar busca. Tente novamente.")

            async def show_payment_popup(self, update: Update, user_id: int, lang: str, is_downsell: bool = False):
                pricing = user_db.get_pricing(lang)
                if is_downsell:
                    copies = {
                        'pt': "🎁 **ESPERA! OFERTA ESPECIAL...**\n\nLiberei o **Plano Semanal** com 30% de desconto! 😱",
                        'es': "🎁 **¡ESPERA! OFERTA ESPECIAL...**\n\n¡Liberé el **Plan Semanal** con 30% de descuento! 😱",
                        'en': "🎁 **WAIT! SPECIAL OFFER...**\n\nI've unlocked the **Weekly Plan** with 30% discount! 😱"
                    }
                    keyboard = [[InlineKeyboardButton(f"⚡ ACEITAR OFERTA - {pricing['weekly']['label']}", callback_data="buy:weekly_ds")]]
                else:
                    copies = {
                        'pt': "🔥 **CONTEÚDO EXCLUSIVO!**\n\nAssine agora e tenha acesso a **100% dos conteúdos**! 🔞",
                        'es': "🔥 **¡CONTENIDO EXCLUSIVO!**\n\n¡Suscríbete ahora y obtén acceso al **100%**! 🔞",
                        'en': "🔥 **EXCLUSIVE CONTENT!**\n\nSubscribe now and get access to **100%**! 🔞"
                    }
                    keyboard = [
                        [InlineKeyboardButton(f"💎 Vitalício - {pricing['lifetime']['label']}", callback_data="buy:lifetime")],
                        [InlineKeyboardButton(f"📅 Mensal - {pricing['monthly']['label']}", callback_data="buy:monthly")],
                        [InlineKeyboardButton(f"⏳ Semanal - {pricing['weekly']['label']}", callback_data="buy:weekly")]
                    ]
                
                msg = update.message if update.message else update.callback_query.message
                await msg.reply_text(copies.get(lang, copies['pt']), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

            async def on_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                query = update.callback_query
                await query.answer()
                user_id = update.effective_user.id
                data = query.data
                u_data = user_db.get_user(user_id)
                lang = u_data.get('language', 'pt')

                if data.startswith("sel:"):
                    _, service, c_id, name = data.split(":")
                    await query.edit_message_text(f"🔄 Carregando mídias de **{name}**...")
                    
                    async with MediaFetcher() as fetcher:
                        creator = {'service': service, 'id': c_id, 'name': name}
                        items = await fetcher.fetch_posts_paged(creator, offset=0)
                        
                        if not items:
                            await query.edit_message_text("❌ Nenhuma mídia encontrada.")
                            return
                        
                        if user_db.is_license_active(user_id):
                            text = f"✅ **{name}** encontrada!\n\nComo você é **VIP**, pode baixar tudo ou navegar."
                            kb = [
                                [InlineKeyboardButton("🚀 BAIXAR TUDO (Lote 50)", callback_data=f"dlall:{service}:{c_id}:{name[:20]}")],
                                [InlineKeyboardButton("📄 Ver Primeira Página", callback_data=f"dlpage:{service}:{c_id}:0:{name[:20]}")]
                            ]
                            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
                        else:
                            user_db.increment_previews(user_id)
                            await query.edit_message_text(f"📤 Enviando 3 prévias de **{name}**...")
                            for item in items[:3]:
                                if await fetcher.download_media(item):
                                    await self.uploader.upload_and_cleanup(item, user_id, caption=f"🔥 Preview: {name}")
                                    await asyncio.sleep(1.5)
                            await self.show_payment_popup(update, user_id, lang)

                elif data.startswith("dlall:") or data.startswith("dlpage:"):
                    parts = data.split(":")
                    action, service, c_id, name = parts[0], parts[1], parts[2], parts[3]
                    offset = int(parts[4]) if action == "dlpage" else 0
                    
                    await query.edit_message_text(f"⏳ Baixando **{name}** em lotes...")
                    async with MediaFetcher() as fetcher:
                        creator = {'service': service, 'id': c_id, 'name': name}
                        items = await fetcher.fetch_posts_paged(creator, offset=offset)
                        if not items:
                            await query.edit_message_text("❌ Nada encontrado.")
                            return
                        
                        for i in range(0, len(items), 10):
                            batch = items[i:i+10]
                            for item in batch:
                                if await fetcher.download_media(item):
                                    await self.uploader.upload_and_cleanup(item, user_id, caption=f"✅ {name} - VIP")
                                    await asyncio.sleep(1.2)
                            await asyncio.sleep(3)
                        await query.message.reply_text(f"✅ Download de {len(items)} mídias concluído!")

                elif data.startswith("buy:"):
                    plan_raw = data.split(":")[1]
                    is_ds = plan_raw.endswith("_ds")
                    plan = plan_raw.replace("_ds", "")
                    pricing = user_db.get_pricing(lang)[plan]
                    price = pricing['price'] * 0.7 if is_ds else pricing['price']
                    
                    order = paypal_client.create_order(price, pricing['currency'], "https://t.me/YourBot", "https://t.me/YourBot")
                    if order:
                        link = next(l['href'] for l in order['links'] if l['rel'] == 'approve')
                        kb = [[InlineKeyboardButton("💳 Pagar com PayPal", url=link)]]
                        await query.edit_message_text(f"✅ Ordem criada! Pague {pricing['label']} via PayPal.", reply_markup=InlineKeyboardMarkup(kb))
                    else:
                        await query.edit_message_text("❌ Erro ao gerar pagamento.")

        # 4. Initialize Application
        app = Application.builder().token(config.BOT_TOKEN).build()
        uploader = TelegramUploader(app.bot)
        bot_logic = VIPBotPV(app, uploader)

        # 5. Register Handlers
        app.add_handler(CommandHandler("start", bot_logic.cmd_start))
        app.add_handler(CommandHandler("search", bot_logic.cmd_search))
        app.add_handler(CallbackQueryHandler(bot_logic.on_callback_query))
        
        logger.info("✅ Bot Handlers registered. Starting polling...")
        
        # 6. Run Polling
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        # Keep the bot running
        while True:
            await asyncio.sleep(3600)

    except Exception as e:
        logger.critical(f"💥 CRITICAL CRASH: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.critical(f"Fatal error in main loop: {e}")
