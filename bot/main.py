"""
Main bot module - v2.1
Telegram VIP Media Bot - Main entry point
"""

import logging
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)

from config import config
from admin import (
    cmd_setvip, cmd_setfreept, cmd_setfreees, cmd_setfreeen,
    cmd_setsubbot_pt, cmd_setsubbot_es, cmd_setsubbot_en,
    cmd_setsource, cmd_setpreview, cmd_setpreviewlimit, cmd_setlang,
    cmd_stats, cmd_restart, cmd_help,
    cmd_addadmin, cmd_removeadmin, cmd_listadmins
)
from fetcher import MediaFetcher
from uploader import TelegramUploader
from preview import PreviewGenerator
from languages import get_text
from users import user_manager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def escape_markdown(text: str) -> str:
    """Escape special characters for Telegram Markdown"""
    if not text:
        return text
    # Characters that need to be escaped in Markdown
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


class VIPBot:
    """Main bot class"""
    
    def __init__(self):
        self.app: Application = None
        self.uploader: TelegramUploader = None
        self.search_cache = {}
    
    async def check_authorization(self, update: Update) -> bool:
        """Check if user is authorized to use the bot"""
        user_id = update.effective_user.id
        
        if not config.is_authorized(user_id):
            await update.message.reply_text(
                "❌ **Acesso Negado**\n\n"
                "Este bot é privado e restrito a usuários autorizados.\n\n"
                "Se você acredita que deveria ter acesso, entre em contato com o administrador.",
                parse_mode="Markdown"
            )
            logger.warning(f"Unauthorized access attempt by user {user_id}")
            return False
        return True
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not await self.check_authorization(update):
            return
        
        user = update.effective_user
        user_manager.get_user(user.id)
        
        welcome_message = f"""
👋 Olá, {user.first_name}!

🤖 **Bot de Mídias VIP**

Este bot busca e distribui mídias de modelos/criadores.

Use /search <nome> para buscar uma modelo.
Use /help para ver todos os comandos.
        """
        
        await update.message.reply_text(welcome_message, parse_mode="Markdown")
    
    async def cmd_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        if not await self.check_authorization(update):
            return
        
        user_id = update.effective_user.id
        lang = user_manager.get_language(user_id)
        
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(get_text("search_usage", lang))
            return
        
        model_name = " ".join(context.args)
        user_manager.increment_searches(user_id)
        
        # Ask user to select source
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("🔵 Coomer.st", callback_data=f"source:coomer:{model_name}")],
            [InlineKeyboardButton("🟠 Picazor.com", callback_data=f"source:picazor:{model_name}")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        status_msg = await update.message.reply_text(
            f"🔍 **Buscar: {escape_markdown(model_name)}**\n\n"
            f"Selecione a fonte de mídias:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    async def _show_page(self, update: Update, user_id: int, page_idx: int, status_msg=None):
        """Show a page of results"""
        cache = self.search_cache.get(user_id)
        if not cache:
            return

        items = cache['pages'].get(page_idx, [])
        count = len(items)
        model_name = cache['model_name']
        total_posts = cache.get('total_posts', 0)
        total_uploaded = cache.get('total_uploaded', 0)
        
        # Calculate estimated total pages
        estimated_pages = (total_posts // 50) + 1 if total_posts > 0 else "?"
        
        text = f"✅ **{escape_markdown(model_name)}**\n\n"
        text += f"📄 Página: {page_idx + 1}/{estimated_pages}\n"
        text += f"📦 Mídias neste slot: {count}\n"
        text += f"📊 Total de posts: {total_posts}\n"
        text += f"✅ Já enviados: {total_uploaded}\n\n"
        text += "Escolha uma opção abaixo:"

        buttons = []
        
        if count > 0:
            buttons.append([
                InlineKeyboardButton(f"📥 Download Página {page_idx + 1}", callback_data=f"dl_{page_idx}")
            ])
            buttons.append([
                InlineKeyboardButton("🚀 Download TUDO (Automático)", callback_data=f"dlall_{page_idx}")
            ])
        
        nav_row = []
        if page_idx > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"page_{page_idx-1}"))
        nav_row.append(InlineKeyboardButton("➡️ Próxima", callback_data=f"page_{page_idx+1}"))
        buttons.append(nav_row)
        
        buttons.append([InlineKeyboardButton("🛑 Parar e Enviar Previews", callback_data="stop_send_previews")])
            
        reply_markup = InlineKeyboardMarkup(buttons)
        
        if status_msg:
            await status_msg.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def on_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        if data.startswith("source:"):
            # Handle source selection
            parts = data.split(":")
            if len(parts) >= 3:
                source = parts[1]  # 'coomer' or 'picazor'
                model_name = ":".join(parts[2:])  # Rejoin in case model name has ':'
                
                await query.edit_message_text(
                    f"🔍 Buscando **{escape_markdown(model_name)}** em {source.capitalize()}...",
                    parse_mode="Markdown"
                )
                
                try:
                    from source_handler import SourceHandler
                    
                    # Find creator in selected source
                    creator = await SourceHandler.search_source(source, model_name)
                    
                    if not creator:
                        # Show similar matches if available
                        matches = await SourceHandler.find_all_matching(source, model_name)
                        if matches:
                            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                            
                            text = f"🔍 Encontramos **{len(matches)}** modelo(s) similar(es) a '{escape_markdown(model_name)}' em {source.capitalize()}:\n\n"
                            text += "Selecione a modelo correta:"
                            
                            keyboard = []
                            for m in matches[:8]:  # Max 8 options
                                creator_name = m.get('name')
                                button_text = f"{creator_name}"
                                callback_data = f"select_model_src:{source}:{creator_name}"
                                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
                            
                            keyboard.append([InlineKeyboardButton("❌ Cancelar", callback_data="cancel_search")])
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            
                            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
                        else:
                            await query.edit_message_text(f"❌ Nenhuma modelo encontrada para '{model_name}' em {source.capitalize()}.")
                        return
                    
                    # Creator found, fetch first page
                    creator_name = creator.get('name')
                    
                    await query.edit_message_text(
                        f"✅ Encontrado: **{escape_markdown(creator_name)}** ({source.capitalize()})\n🔄 Carregando mídias...",
                        parse_mode="Markdown"
                    )
                    
                    # Fetch first page
                    first_page_items = await SourceHandler.fetch_posts(source, creator, offset=0)
                    
                    if not first_page_items:
                        await query.edit_message_text(
                            f"❌ Nenhuma mídia encontrada para **{escape_markdown(creator_name)}**",
                            parse_mode="Markdown"
                        )
                        return
                    
                    # Store in cache
                    self.search_cache[user_id] = {
                        'model_name': creator_name,
                        'creator': creator,
                        'source': source,
                        'pages': {0: first_page_items},
                        'current_page': 0,
                        'total_sent': 0,
                        'total_uploaded': 0,
                        'uploaded_items': [],
                        'sent_media_ids': set(),
                        'abort_flag': False  # Flag to abort downloads
                    }
                    
                    await self._show_page(update, user_id, 0)
                
                except Exception as e:
                    logger.error(f"Error searching {source}: {e}")
                    await query.edit_message_text(f"❌ Erro: {e}")
            return
        
        if data.startswith("select_model_src:"):
            # Handle model selection with source
            parts = data.split(":")
            if len(parts) >= 3:
                source = parts[1]
                creator_name = ":".join(parts[2:])
                
                await query.edit_message_text(
                    f"✅ Modelo selecionada: **{escape_markdown(creator_name)}**\n🔄 Carregando mídias...",
                    parse_mode="Markdown"
                )
                
                try:
                    from source_handler import SourceHandler
                    
                    creator = await SourceHandler.search_source(source, creator_name)
                    
                    if not creator:
                        await query.message.reply_text("❌ Erro ao carregar modelo.")
                        return
                    
                    # Get first page
                    first_page_items = await SourceHandler.fetch_posts(source, creator, offset=0)
                    
                    if not first_page_items:
                        await query.message.reply_text(
                            f"❌ Nenhuma mídia encontrada para **{escape_markdown(creator_name)}**",
                            parse_mode="Markdown"
                        )
                        return
                    
                    # Store in cache
                    self.search_cache[user_id] = {
                        'model_name': creator_name,
                        'creator': creator,
                        'source': source,
                        'pages': {0: first_page_items},
                        'current_page': 0,
                        'total_sent': 0,
                        'total_uploaded': 0,
                        'uploaded_items': [],
                        'sent_media_ids': set(),
                        'abort_flag': False
                    }
                    
                    await self._show_page(update, user_id, 0)
                except Exception as e:
                    logger.error(f"Error loading selected model: {e}")
                    await query.message.reply_text(f"❌ Erro: {e}")
            return
        
        if data.startswith("select_model:"):
            # Handle model selection from search results
            parts = data.split(":")
            if len(parts) >= 3:
                creator_name = parts[1]
                service = parts[2]
                
                await query.edit_message_text(
                    f"✅ Modelo selecionada: **{creator_name}** ({service})\n🔄 Carregando mídias...",
                    parse_mode="Markdown"
                )
                
                # Simulate a search with the selected creator
                try:
                    async with MediaFetcher() as fetcher:
                        creator = await fetcher.find_creator(creator_name)
                        
                        if not creator:
                            await query.message.reply_text("❌ Erro ao carregar modelo.")
                            return
                        
                        # Get first page
                        first_page_items = await fetcher.fetch_posts_paged(creator, offset=0)
                        
                        if not first_page_items:
                            await query.message.reply_text(
                                f"❌ Nenhuma mídia encontrada para **{creator_name}**",
                                parse_mode="Markdown"
                            )
                            return
                        
                        # Store in cache
                        self.search_cache[user_id] = {
                            'model_name': creator_name,
                            'creator': creator,
                            'pages': {0: first_page_items},
                            'current_page': 0,
                            'total_sent': 0,
                            'sent_media_ids': set()
                        }
                        
                        await self._show_page(update, user_id, 0)
                except Exception as e:
                    logger.error(f"Error loading selected model: {e}")
                    await query.message.reply_text(f"❌ Erro: {e}")
            return
        
        if data == "cancel_search":
            await query.edit_message_text("❌ Busca cancelada.")
            return
        
        if data == "abort_download":
            # Set abort flag
            cache = self.search_cache.get(user_id)
            if cache:
                cache['abort_flag'] = True
                await query.answer("⛔ Abortando download...", show_alert=True)
            return
        
        if data == "stop_send_previews":
            await self._finalize_and_send_previews(update, user_id)
            return
        
        if data.startswith("page_"):
            page_idx = int(data.split("_")[1])
            cache = self.search_cache.get(user_id)
            if not cache:
                await query.edit_message_text("❌ Sessão expirada. Use /search novamente.")
                return

            # If page not in cache, fetch it
            if page_idx not in cache['pages']:
                await query.edit_message_text("🔄 Carregando página...")
                
                try:
                    async with MediaFetcher() as fetcher:
                        new_offset = page_idx * 50
                        new_items = await fetcher.fetch_posts_paged(cache['creator'], offset=new_offset)
                        
                        if not new_items:
                            await query.message.reply_text("❌ Não há mais mídias disponíveis.")
                            await self._show_page(update, user_id, max(0, page_idx - 1))
                            return
                        
                        cache['pages'][page_idx] = new_items
                        logger.info(f"Page {page_idx} loaded with {len(new_items)} items")
                except Exception as e:
                    logger.error(f"Error fetching page: {e}")
                    await query.edit_message_text(f"❌ Erro ao carregar página: {e}")
                    return
            
            await self._show_page(update, user_id, page_idx)
            
        elif data.startswith("dl_"):
            page_idx = int(data.split("_")[1])
            await self._process_download_slot(update, user_id, page_idx, auto_continue=False)
            
        elif data.startswith("dlall_"):
            page_idx = int(data.split("_")[1])
            await self._process_download_slot(update, user_id, page_idx, auto_continue=True)

    async def _process_download_slot(self, update: Update, user_id: int, page_idx: int, auto_continue: bool = False):
        """Process download and upload for a specific page"""
        cache = self.search_cache.get(user_id)
        
        if not cache:
            await update.callback_query.edit_message_text("❌ Sessão expirada. Use /search novamente.")
            return

        slot_items = cache['pages'].get(page_idx, [])
        if not slot_items:
            await update.callback_query.edit_message_text("❌ Nenhuma mídia neste slot.")
            return
            
        model_name = cache['model_name']
        status_msg = update.callback_query.message
        
        await status_msg.edit_text(
            f"⏳ **Iniciando Slot {page_idx + 1}**\n"
            f"📦 Mídias: {len(slot_items)}\n"
            f"🔄 Conectando aos servidores...",
            parse_mode="Markdown"
        )
        
        vip_count = 0
        failed_count = 0
        total_in_slot = len(slot_items)
        
        async with MediaFetcher() as fetcher:
            for i, item in enumerate(slot_items):
                # Check abort flag
                if cache.get('abort_flag', False):
                    await status_msg.edit_text(
                        f"⛔ **Download Abortado pelo Usuário**\n\n"
                        f"✅ Enviados: {vip_count}\n"
                        f"❌ Falhas: {failed_count}\n\n"
                        f"Use /search para iniciar nova busca.",
                        parse_mode="Markdown"
                    )
                    return
                
                try:
                    # Update progress
                    progress_pct = ((i + 1) / total_in_slot) * 100
                    progress_bar = "█" * int(progress_pct / 10) + "░" * (10 - int(progress_pct / 10))
                    
                    progress_text = f"📥 **Processando Slot {page_idx + 1}**\n\n"
                    progress_text += f"[{progress_bar}] {progress_pct:.0f}%\n"
                    progress_text += f"📊 {i+1}/{total_in_slot}\n"
                    progress_text += f"✅ Enviados: {vip_count}\n"
                    progress_text += f"❌ Falhas: {failed_count}\n\n"
                    progress_text += f"📦 `{item.filename[:35]}...`"
                    
                    # Add abort button
                    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                    abort_button = InlineKeyboardMarkup([
                        [InlineKeyboardButton("⛔ Abortar Download", callback_data="abort_download")]
                    ])
                    
                    try:
                        await status_msg.edit_text(progress_text, parse_mode="Markdown", reply_markup=abort_button)
                    except:
                        pass
                    
                    # Download
                    success = await fetcher.download_media(item)
                    
                    if not success:
                        logger.warning(f"Failed to download: {item.url}")
                        failed_count += 1
                        continue
                    
                    # Upload to VIP channel
                    uploaded = await self.uploader.upload_and_cleanup(
                        item,
                        config.VIP_CHANNEL_ID,
                        caption=f"🔥 **{escape_markdown(model_name)}**"
                    )
                    
                    if uploaded:
                        vip_count += 1
                        cache['total_uploaded'] += 1
                        # Store item info for previews later
                        cache['uploaded_items'].append({
                            'url': item.url,
                            'type': item.media_type,
                            'filename': item.filename
                        })
                    else:
                        failed_count += 1

                    # Delay to avoid rate limits (2 seconds between uploads)
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing item {i}: {e}")
                    failed_count += 1

        # Slot complete
        final_text = f"✅ **Slot {page_idx + 1} Concluído!**\n\n"
        final_text += f"📊 **Resultados:**\n"
        final_text += f"✅ Enviados: {vip_count}\n"
        final_text += f"❌ Falhas: {failed_count}\n"
        final_text += f"📈 Total enviados: {cache['total_uploaded']}\n"
        
        await status_msg.edit_text(final_text, parse_mode="Markdown")
        await asyncio.sleep(2)
        
        # Auto-continue to next page if enabled
        if auto_continue:
            next_page = page_idx + 1
            
            # Fetch next page
            async with MediaFetcher() as fetcher:
                new_offset = next_page * 50
                new_items = await fetcher.fetch_posts_paged(cache['creator'], offset=new_offset)
                
                if new_items:
                    cache['pages'][next_page] = new_items
                    await status_msg.edit_text(
                        f"🔄 **Continuando automaticamente...**\n"
                        f"Próxima página: {next_page + 1}\n"
                        f"Mídias: {len(new_items)}",
                        parse_mode="Markdown"
                    )
                    await asyncio.sleep(3)  # Delay between pages
                    await self._process_download_slot(update, user_id, next_page, auto_continue=True)
                    return
                else:
                    # No more pages, finalize
                    await self._finalize_and_send_previews(update, user_id)
                    return
        
        # Show page again
        await self._show_page(update, user_id, page_idx, status_msg)

    async def _finalize_and_send_previews(self, update: Update, user_id: int):
        """Finalize the process and send previews to FREE channels"""
        cache = self.search_cache.get(user_id)
        
        if not cache:
            await update.callback_query.edit_message_text("❌ Sessão expirada.")
            return
        
        model_name = cache['model_name']
        total_uploaded = cache.get('total_uploaded', 0)
        uploaded_items = cache.get('uploaded_items', [])
        status_msg = update.callback_query.message
        
        await status_msg.edit_text(
            f"🏁 **Finalizando...**\n\n"
            f"📊 Total enviados para VIP: {total_uploaded}\n"
            f"🖼️ Encaminhando previews aleatórias do VIP para canais FREE...",
            parse_mode="Markdown"
        )
        
        # Send previews by forwarding from VIP
        preview_count = 0
        
        if total_uploaded > 0:
            try:
                await self.uploader.send_previews_from_vip(model_name)
                preview_count = config.get_value("PREVIEW_LIMIT", 3)
                
                await status_msg.edit_text(
                    f"✅ **Previews enviados com sucesso!**\n\n"
                    f"📊 {preview_count} mídias aleatórias encaminhadas para os canais FREE.",
                    parse_mode="Markdown"
                )
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error forwarding previews: {e}")
                await status_msg.edit_text(
                    f"⚠️ Erro ao enviar previews: {e}",
                    parse_mode="Markdown"
                )
                await asyncio.sleep(2)
        
        # Final summary
        final_text = f"🎉 **Processo Concluído!**\n\n"
        final_text += f"👤 Modelo: **{model_name}**\n"
        final_text += f"✅ Mídias enviadas para VIP: {total_uploaded}\n"
        final_text += f"🖼️ Previews enviados para FREE: {preview_count}\n\n"
        final_text += "Use /search para buscar outra modelo."
        
        await status_msg.edit_text(final_text, parse_mode="Markdown")
        
        # Clear cache
        if user_id in self.search_cache:
            del self.search_cache[user_id]
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", cmd_help))
        self.app.add_handler(CommandHandler("search", self.cmd_search))
        self.app.add_handler(CallbackQueryHandler(self.on_callback_query))
        
        # Admin commands
        self.app.add_handler(CommandHandler("setvip", cmd_setvip))
        self.app.add_handler(CommandHandler("setfreept", cmd_setfreept))
        self.app.add_handler(CommandHandler("setfreees", cmd_setfreees))
        self.app.add_handler(CommandHandler("setfreeen", cmd_setfreeen))
        self.app.add_handler(CommandHandler("setsubbot_pt", cmd_setsubbot_pt))
        self.app.add_handler(CommandHandler("setsubbot_es", cmd_setsubbot_es))
        self.app.add_handler(CommandHandler("setsubbot_en", cmd_setsubbot_en))
        self.app.add_handler(CommandHandler("setsource", cmd_setsource))
        self.app.add_handler(CommandHandler("setpreview", cmd_setpreview))
        self.app.add_handler(CommandHandler("setpreviewlimit", cmd_setpreviewlimit))
        self.app.add_handler(CommandHandler("setlang", cmd_setlang))
        self.app.add_handler(CommandHandler("stats", cmd_stats))
        self.app.add_handler(CommandHandler("restart", cmd_restart))
        
        # Whitelist management commands
        self.app.add_handler(CommandHandler("addadmin", cmd_addadmin))
        self.app.add_handler(CommandHandler("removeadmin", cmd_removeadmin))
        self.app.add_handler(CommandHandler("listadmins", cmd_listadmins))
    
    async def post_init(self, application: Application):
        """Post initialization callback"""
        logger.info("Bot initialized successfully")
        self.uploader = TelegramUploader(application.bot)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
    
    def run(self):
        """Run the bot"""
        if not config.validate():
            logger.error("Invalid configuration. Please check your .env file")
            return
        
        self.app = Application.builder().token(config.BOT_TOKEN).build()
        self.setup_handlers()
        self.app.add_error_handler(self.error_handler)
        self.app.post_init = self.post_init
        
        logger.info("Starting bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("Telegram VIP Media Bot v2.1")
    logger.info("=" * 50)
    
    bot = VIPBot()
    bot.run()


if __name__ == "__main__":
    main()
