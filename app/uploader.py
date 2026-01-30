"""
Uploader module
Handles uploading media to Telegram channels with rate limiting
"""

import os
import logging
import asyncio
import random
from typing import List, Optional, Set
from telegram import Bot, InputMediaPhoto, InputMediaVideo
from telegram.error import TelegramError, RetryAfter, TimedOut
from telegram.constants import ParseMode
from html import escape as escape_html
from app.fetcher import MediaItem
from app.config import Config
config = Config()

logger = logging.getLogger(__name__)
import aiofiles
import io
import os

# Max Telegram file size for uploads (safety margin)
MAX_TELEGRAM_FILE_SIZE = 49 * 1024 * 1024  # 49 MB


class TelegramUploader:
    """Handles uploading media to Telegram channels"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.vip_message_ids: List[int] = []  # Store VIP message IDs for forwarding
    
    async def upload_to_vip(self, media_items: List[MediaItem], 
                           progress_callback=None) -> int:
        """
        Upload media items to VIP channel and store message IDs
        
        Args:
            media_items: List of MediaItem objects with local_path set
            progress_callback: Optional callback for progress updates
        
        Returns:
            Number of successfully uploaded items
        """
        if not config.VIP_CHANNEL_ID:
            logger.error("VIP channel ID not configured")
            return 0
        
        uploaded_count = 0
        total = len(media_items)
        batch_size = config.MAX_FILES_PER_BATCH
        
        # Split into batches
        for i in range(0, total, batch_size):
            batch = media_items[i:i + batch_size]
            
            try:
                # Upload batch and get message IDs
                message_ids = await self._upload_batch(
                    config.VIP_CHANNEL_ID,
                    batch,
                    caption="🔥 Conteúdo VIP"
                )
                
                if message_ids:
                    uploaded_count += len(batch)
                    self.vip_message_ids.extend(message_ids)
                
                if progress_callback:
                    await progress_callback(i + len(batch), total)
                
                # Rate limiting between batches
                await asyncio.sleep(2)
            
            except Exception as e:
                logger.error(f"Error uploading batch to VIP: {e}")
        
        logger.info(f"Uploaded {uploaded_count}/{total} items to VIP channel")
        logger.info(f"Stored {len(self.vip_message_ids)} VIP message IDs for previews")
        return uploaded_count
    
    async def _upload_batch(self, channel_id: int, media_items: List[MediaItem],
                           caption: str = "") -> List[int]:
        """
        Upload a batch of media items to a channel
        
        Args:
            channel_id: Telegram channel ID
            media_items: List of MediaItem objects
            caption: Caption for the media group
        
        Returns:
            List of message IDs if successful, empty list otherwise
        """
        if not media_items:
            return []
        
        try:
            # If single item, send directly
            if len(media_items) == 1:
                msg_id = await self._upload_single(channel_id, media_items[0], caption)
                return [msg_id] if msg_id else []
            
            # Multiple items: create media group
            media_group = []
            
            for item in media_items:
                if not item.local_path or not os.path.exists(item.local_path):
                    logger.warning(f"File not found: {item.local_path}")
                    continue

                try:
                    size = os.path.getsize(item.local_path)
                    if size == 0:
                        logger.warning(f"File empty, skipping: {item.local_path}")
                        continue
                    if size > MAX_TELEGRAM_FILE_SIZE:
                        logger.warning(f"File too large (>49MB), skipping: {item.local_path} ({size} bytes)")
                        continue

                    async with aiofiles.open(item.local_path, 'rb') as f:
                        data = await f.read()
                    if not data:
                        logger.warning(f"File has no data, skipping: {item.local_path}")
                        continue
                    bio = io.BytesIO(data)
                    bio.name = os.path.basename(item.local_path)
                    if item.media_type == "video":
                        media_group.append(InputMediaVideo(bio))
                    else:
                        media_group.append(InputMediaPhoto(bio))
                except Exception as e:
                    logger.warning(f"Failed to read file async for upload {item.local_path}: {e}")
                    continue
            
            if not media_group:
                return []
            
            # Add caption to first item
            if media_group and caption:
                media_group[0].caption = caption
                media_group[0].parse_mode = ParseMode.HTML
            
            # Send media group with retry logic
            messages = await self._send_with_retry(
                lambda: self.bot.send_media_group(
                    chat_id=channel_id,
                    media=media_group
                )
            )
            
            # Extract message IDs
            message_ids = [msg.message_id for msg in messages] if messages else []
            return message_ids
        
        except Exception as e:
            logger.error(f"Error uploading batch: {e}")
            return []
    
    async def _upload_single(self, channel_id: int, media_item: MediaItem,
                            caption: str = "", reply_markup=None) -> Optional[int]:
        """
        Upload a single media item
        
        Args:
            channel_id: Telegram channel ID
            media_item: MediaItem object
            caption: Caption for the media
        
        Returns:
            Message ID if successful, None otherwise
        """
        if not media_item.local_path or not os.path.exists(media_item.local_path):
            logger.warning(f"File not found: {media_item.local_path}")
            return None
        
        try:
            size = os.path.getsize(media_item.local_path) if media_item.local_path and os.path.exists(media_item.local_path) else 0
            if size == 0:
                logger.warning(f"File empty, skipping upload: {media_item.local_path}")
                return None
            if size > MAX_TELEGRAM_FILE_SIZE:
                logger.warning(f"File too large (>49MB), skipping upload: {media_item.local_path} ({size} bytes)")
                return None

            async with aiofiles.open(media_item.local_path, 'rb') as f:
                data = await f.read()
            if not data:
                logger.warning(f"Read zero bytes from file, aborting upload: {media_item.local_path}")
                return None
            bio = io.BytesIO(data)
            bio.name = os.path.basename(media_item.local_path)
            if media_item.media_type == "video":
                    msg = await self._send_with_retry(
                        lambda: self.bot.send_video(
                            chat_id=channel_id,
                            video=bio,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup
                        )
                    )
            else:
                msg = await self._send_with_retry(
                    lambda: self.bot.send_photo(
                        chat_id=channel_id,
                        photo=bio,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup
                    )
                )

            return msg.message_id if msg else None
        
        except Exception as e:
            logger.error(f"Error uploading single item: {e}")
            return None
    
    async def send_previews_from_vip(self, model_name: str, max_previews: int = None):
        """
        Forward random previews from VIP channel to FREE channels with copy
        
        Args:
            model_name: Name of the model for the caption
            max_previews: Maximum number of previews to send (default from config)
        """
        if not self.vip_message_ids:
            logger.warning("No VIP messages to forward as previews")
            return
        
        max_previews = max_previews or config.get_value('PREVIEW_LIMIT', 3)
        
        # Select random message IDs
        preview_count = min(max_previews, len(self.vip_message_ids))
        selected_ids = random.sample(self.vip_message_ids, preview_count)
        
        logger.info(f"Forwarding {preview_count} random previews from VIP")
        
        # Get FREE channel IDs
        free_channels = {
            'pt': config.get_value("FREE_CHANNEL_PT_ID"),
            'es': config.get_value("FREE_CHANNEL_ES_ID"),
            'en': config.get_value("FREE_CHANNEL_EN_ID")
        }
        
        # Forward to each FREE channel
        for lang, channel_id in free_channels.items():
            if not channel_id:
                continue
            
            try:
                # Get subscription bot link for this language
                sub_link = config.get_sub_link_by_lang(lang)
                
                # Create caption with copy
                caption = self._get_preview_caption(model_name, lang, sub_link)
                
                # Forward each selected message
                for msg_id in selected_ids:
                    try:
                        await self.bot.forward_message(
                            chat_id=channel_id,
                            from_chat_id=config.VIP_CHANNEL_ID,
                            message_id=msg_id
                        )
                        
                        # Send caption as separate message
                        await self.bot.send_message(
                            chat_id=channel_id,
                            text=escape_html(caption),
                            parse_mode=ParseMode.HTML
                        )
                        
                        await asyncio.sleep(1)  # Rate limiting
                    
                    except Exception as e:
                        logger.error(f"Error forwarding message {msg_id} to {lang}: {e}")
                
                logger.info(f"Sent {preview_count} previews to FREE {lang.upper()} channel")
            
            except Exception as e:
                logger.error(f"Error sending previews to {lang}: {e}")
        
        # Clear VIP message IDs after forwarding
        self.vip_message_ids.clear()
    
    def _get_preview_caption(self, model_name: str, lang: str, sub_link: str) -> str:
        """Generate preview caption with copy in the specified language"""
        captions = {
            'pt': f"""
🔥 **Preview Exclusiva - {model_name}**

Quer ver TUDO sem censura?

✨ Acesso VIP inclui:
• Conteúdo completo e sem limites
• Atualizações diárias
• Milhares de fotos e vídeos

👉 [CLIQUE AQUI PARA ASSINAR]({sub_link})

⚠️ Vagas limitadas!
""",
            'es': f"""
🔥 **Preview Exclusivo - {model_name}**

¿Quieres verlo TODO sin censura?

✨ El acceso VIP incluye:
• Contenido completo y sin límites
• Actualizaciones diarias
• Miles de fotos y videos

👉 [HAZ CLIC AQUÍ PARA SUSCRIBIRTE]({sub_link})

⚠️ ¡Plazas limitadas!
""",
            'en': f"""
🔥 **Exclusive Preview - {model_name}**

Want to see EVERYTHING uncensored?

✨ VIP access includes:
• Full content with no limits
• Daily updates
• Thousands of photos and videos

👉 [CLICK HERE TO SUBSCRIBE]({sub_link})

⚠️ Limited spots!
"""
        }
        
        return captions.get(lang, captions['pt'])
    
    async def _send_with_retry(self, send_func, max_retries: int = 3):
        """
        Send message with retry logic for rate limiting
        
        Args:
            send_func: Async function to send message
            max_retries: Maximum number of retries
        """
        for attempt in range(max_retries):
            try:
                return await send_func()
            
            except RetryAfter as e:
                # Telegram rate limit hit
                wait_time = e.retry_after + 1
                logger.warning(f"Rate limited. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            
            except TimedOut:
                # Timeout - retry with exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"Timeout. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            
            except TelegramError as e:
                logger.error(f"Telegram error: {e}")
                if attempt == max_retries - 1:
                    raise
        
        return None
    
    async def upload_and_cleanup(self, media_item: MediaItem, channel_id: int, caption: str = "", reply_markup=None) -> bool:
        """
        Upload a single media item and delete it immediately after
        
        Args:
            media_item: MediaItem object with local_path
            channel_id: Target channel ID
            caption: Optional caption
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Upload
            msg_id = await self._upload_single(channel_id, media_item, caption, reply_markup=reply_markup)
            
            if msg_id:
                # Store message ID if uploading to VIP
                if channel_id == config.VIP_CHANNEL_ID:
                    self.vip_message_ids.append(msg_id)
            
            # Delete local file
            if media_item.local_path and os.path.exists(media_item.local_path):
                try:
                    os.remove(media_item.local_path)
                    logger.debug(f"Deleted: {media_item.local_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete {media_item.local_path}: {e}")
            
            return msg_id is not None
        
        except Exception as e:
            logger.error(f"Error in upload_and_cleanup: {e}")
            return False
