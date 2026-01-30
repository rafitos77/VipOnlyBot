"""
Main bot module - PV Version
Telegram VIP Media Bot - Direct User Delivery
"""

import logging
import asyncio
import os
import sys
from datetime import datetime

# Garante que o diretório atual esteja no path para evitar ModuleNotFoundError no Railway
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

from config import config
from fetcher import MediaFetcher
from uploader import TelegramUploader
from languages import get_text
from users_db import user_db
from smart_search import smart_search
from paypal_integration import paypal_client

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    if not text: return text
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

class VIPBotPV:
    def __init__(self):
        self.app: Application = None
        self.uploader: TelegramUploader = None
        self.search_cache = {}

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

        # Check preview limit (Admins are always allowed)
        if user_id != config.ADMIN_ID and not user_db.check_preview_limit(user_id):
            await self.show_payment_popup(update, user_id, lang)
            return

        model_name = " ".join(context.args)
        status_msg = await update.message.reply_text(f"🔍 {get_text('searching', lang, name=model_name)}")

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

    async def show_payment_popup(self, update: Update, user_id: int, lang: str, is_downsell: bool = False):
        pricing = user_db.get_pricing(lang)
        
        if is_downsell:
            copies = {
                'pt': "🎁 **ESPERA! UMA OFERTA ESPECIAL...**\n\nVi que você se interessou mas não concluiu. Para você não ficar de fora, liberei o **Plano Semanal** por um preço ainda mais baixo! 😱\n\n⚠️ *Válido pelos próximos 15 minutos!*",
                'es': "🎁 **¡ESPERA! UNA OFERTA ESPECIAL...**\n\nVi que te interesaste pero no completaste. ¡Para que no te quedes fuera, liberé el **Plan Semanal** a un precio aún más bajo! 😱\n\n⚠️ *¡Válido por los próximos 15 minutos!*",
                'en': "🎁 **WAIT! A SPECIAL OFFER...**\n\nI saw you were interested but didn't finish. To make sure you don't miss out, I've unlocked the **Weekly Plan** at an even lower price! 😱\n\n⚠️ *Valid for the next 15 minutes!*"
            }
            # Downsell: Weekly price reduced by 30% for the button label (logic would need to handle this in buy:)
            keyboard = [[InlineKeyboardButton(f"⚡ ACEITAR OFERTA AGORA - {pricing['weekly']['label']}", callback_data="buy:weekly_ds")]]
        else:
            copies = {
                'pt': "🔥 **CONTEÚDO EXCLUSIVO LIBERADO!**\n\nVocê atingiu o limite grátis, mas o melhor ainda está por vir. Assine agora e tenha acesso a **100% dos conteúdos** sem censura! 🔞\n\n⏱️ **SENSO DE URGÊNCIA:** Apenas 5 vagas restantes com este preço promocional!",
                'es': "🔥 **¡CONTENIDO EXCLUSIVO LIBERADO!**\n\nHas alcanzado el límite gratuito, pero lo mejor está por venir. ¡Suscríbete ahora y obtén acceso al **100% de los contenidos** sin censura! 🔞\n\n⏱️ **SENTIDO DE URGENCIA:** ¡Solo quedan 5 cupos con este precio promocional!",
                'en': "🔥 **EXCLUSIVE CONTENT UNLOCKED!**\n\nYou've reached the free limit, but the best is yet to come. Subscribe now and get access to **100% of the content** uncensored! 🔞\n\n⏱️ **SENSE OF URGENCY:** Only 5 spots left at this promotional price!"
            }
            keyboard = [
                [InlineKeyboardButton(f"💎 Plano Vitalício (MELHOR VALOR) - {pricing['lifetime']['label']}", callback_data="buy:lifetime")],
                [InlineKeyboardButton(f"📅 Plano Mensal - {pricing['monthly']['label']}", callback_data="buy:monthly")],
                [InlineKeyboardButton(f"⏳ Plano Semanal - {pricing['weekly']['label']}", callback_data="buy:weekly")]
            ]
        
        msg = update.message if update.message else update.callback_query.message
        await msg.reply_text(copies.get(lang, copies['pt']), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

    async def run_remarketing(self, user_id: int, lang: str):
        """Remarketing task to run after a delay"""
        await asyncio.sleep(600) # 10 minutes
        u_data = user_db.get_user(user_id)
        if not u_data.get('is_vip'):
            # Send downsell
            # Note: This requires a way to send message without an active update
            try:
                await self.app.bot.send_message(chat_id=user_id, text="👀") # Placeholder or trigger
                # In a real implementation, we'd call show_payment_popup with is_downsell=True
            except: pass

    async def on_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = update.effective_user.id
        data = query.data
        u_data = user_db.get_user(user_id)
        lang = u_data.get('language', 'pt')

        if data.startswith("sel:"):
            # Model selected
            _, service, c_id, name = data.split(":")
            await query.edit_message_text(f"🔄 Carregando mídias de **{name}**...")
            
            async with MediaFetcher() as fetcher:
                creator = {'service': service, 'id': c_id, 'name': name}
                items = await fetcher.fetch_posts_paged(creator, offset=0)
                
                if not items:
                    await query.edit_message_text("❌ Nenhuma mídia encontrada.")
                    return
                
                # Check license status
                is_vip = user_db.is_license_active(user_id)
                
                if is_vip:
                    # VIP/Admin: Show options for mass download or specific page
                    text = f"✅ **{name}** encontrada!\n\nComo você é um usuário **VIP**, você pode baixar todo o conteúdo de uma vez ou navegar pelas páginas."
                    kb = [
                        [InlineKeyboardButton("🚀 BAIXAR TUDO (Lote de 50)", callback_data=f"dlall:{service}:{c_id}:{name[:20]}")],
                        [InlineKeyboardButton("📄 Ver Primeira Página", callback_data=f"dlpage:{service}:{c_id}:0:{name[:20]}")]
                    ]
                    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
                else:
                    # Free User: Send 3 previews automatically
                    user_db.increment_previews(user_id)
                    await query.edit_message_text(f"📤 Enviando 3 prévias de **{name}** para seu PV...")
                    
                    for item in items[:3]:
                        success = await fetcher.download_media(item)
                        if success:
                            await self.uploader.upload_and_cleanup(item, user_id, caption=f"🔥 Preview: {name}")
                            await asyncio.sleep(1.5) # Safe delay
                    
                    await self.show_payment_popup(update, user_id, lang)

        elif data.startswith("dlall:") or data.startswith("dlpage:"):
            # Mass download logic for VIPs
            parts = data.split(":")
            action = parts[0]
            service = parts[1]
            c_id = parts[2]
            name = parts[3]
            offset = int(parts[4]) if action == "dlpage" else 0
            
            await query.edit_message_text(f"⏳ Iniciando download em massa de **{name}**...\nIsso pode levar alguns minutos. As mídias chegarão em lotes no seu PV.")
            
            async with MediaFetcher() as fetcher:
                creator = {'service': service, 'id': c_id, 'name': name}
                items = await fetcher.fetch_posts_paged(creator, offset=offset)
                
                if not items:
                    await query.edit_message_text("❌ Nenhuma mídia encontrada nesta página.")
                    return
                
                # Process in batches of 10 to avoid Telegram Flood Limits
                batch_size = 10
                for i in range(0, len(items), batch_size):
                    batch = items[i:i+batch_size]
                    for item in batch:
                        success = await fetcher.download_media(item)
                        if success:
                            await self.uploader.upload_and_cleanup(item, user_id, caption=f"✅ {name} - Pack VIP")
                            await asyncio.sleep(1.2) # Anti-flood delay
                    
                    # Small break between batches
                    await asyncio.sleep(3)
                
                await query.message.reply_text(f"✅ **Download de {len(items)} mídias concluído!**\nUse /search para buscar outra modelo.")

        elif data.startswith("buy:"):
            plan_raw = data.split(":")[1]
            is_ds = plan_raw.endswith("_ds")
            plan = plan_raw.replace("_ds", "")
            
            pricing = user_db.get_pricing(lang)[plan]
            price = pricing['price'] * 0.7 if is_ds else pricing['price']
            
            # Start remarketing timer if not a downsell
            if not is_ds:
                asyncio.create_task(self.remarketing_timer(user_id, lang))

            # Create PayPal Order
            order = paypal_client.create_order(
                price, 
                pricing['currency'],
                return_url="https://t.me/YourBot?start=success",
                cancel_url="https://t.me/YourBot?start=cancel"
            )
            
            if order:
                link = next(l['href'] for l in order['links'] if l['rel'] == 'approve')
                text = {
                    'pt': f"✅ Ordem criada! Clique no botão abaixo para pagar {pricing['label']} via PayPal.\n\nApós o pagamento, sua licença será ativada automaticamente.",
                    'es': f"✅ ¡Orden creada! Haz clic en el botón de abajo para pagar {pricing['label']} vía PayPal.\n\nDespués del pago, tu licencia se activará automáticamente.",
                    'en': f"✅ Order created! Click the button below to pay {pricing['label']} via PayPal.\n\nAfter payment, your license will be activated automatically."
                }
                kb = [[InlineKeyboardButton("💳 Pagar com PayPal", url=link)]]
                await query.edit_message_text(text.get(lang, text['pt']), reply_markup=InlineKeyboardMarkup(kb))
            else:
                await query.edit_message_text("❌ Erro ao gerar pagamento. Tente novamente mais tarde.")

    async def remarketing_timer(self, user_id: int, lang: str):
        """Wait 15 minutes and send downsell if not paid"""
        await asyncio.sleep(900) # 15 minutes
        if not user_db.is_license_active(user_id):
            # Trigger downsell
            # We need a dummy update or similar to call show_payment_popup
            # For simplicity in this version, we send a direct message
            pricing = user_db.get_pricing(lang)
            copy = {
                'pt': f"🎁 **OFERTA DE ÚLTIMA HORA!**\n\nVi que você não concluiu seu acesso. Liberei um desconto de **30%** no Plano Semanal só para você!\n\nDe {pricing['weekly']['label']} por apenas **BRL {(pricing['weekly']['price']*0.7):.2f}**!",
                'es': f"🎁 **¡OFERTA DE ÚLTIMA HORA!**\n\nVi que no completaste tu acceso. ¡Liberé un descuento del **30%** en el Plan Semanal solo para ti!\n\n¡De {pricing['weekly']['label']} por solo **USD {(pricing['weekly']['price']*0.7):.2f}**!",
                'en': f"🎁 **LAST MINUTE OFFER!**\n\nI saw you didn't complete your access. I've unlocked a **30% discount** on the Weekly Plan just for you!\n\nFrom {pricing['weekly']['label']} to only **USD {(pricing['weekly']['price']*0.7):.2f}**!"
            }
            kb = [[InlineKeyboardButton("⚡ RESGATAR DESCONTO", callback_data="buy:weekly_ds")]]
            try:
                await self.app.bot.send_message(chat_id=user_id, text=copy.get(lang, copy['pt']), reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
            except: pass

    def run(self):
        self.app = Application.builder().token(config.BOT_TOKEN).build()
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("search", self.cmd_search))
        self.app.add_handler(CallbackQueryHandler(self.on_callback_query))
        
        self.uploader = TelegramUploader(self.app.bot)
        logger.info("Bot PV iniciado...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = VIPBotPV()
    bot.run()
