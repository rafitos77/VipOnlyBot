
"""
Media fetcher module - v8.2 Stealth Edition
Handles searching and downloading media from secret archives
"""

import os
import logging
import asyncio
import aiohttp
import aiofiles
from typing import List, Dict, Any, Optional
from app.config import Config
config = Config()

logger = logging.getLogger(__name__)

# Download directory
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class MediaItem:
    """Represents a media item"""
    
    def __init__(self, url: str, filename: str, media_type: str = "photo", post_id: str = None):
        self.url = url
        self.filename = filename
        self.media_type = media_type  # photo or video
        self.post_id = post_id
        self.local_path: Optional[str] = None
    
    def __repr__(self):
        return f"MediaItem(url={self.url}, type={self.media_type}, post={self.post_id})"


class MediaFetcher:
    """Fetches media from secret archives using validated APIs"""
    
    # Source URL hidden from logs and messages
    BASE_URL = "https://coomer.st"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/css',
        }
        self._creators_cache = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=180),
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _get_creators_list(self) -> List[Dict]:
        """Get and cache the full creators list"""
        if self._creators_cache is not None:
            return self._creators_cache
        
        try:
            url = f"{self.BASE_URL}/api/v1/creators"
            async with self.session.get(url) as response:
                if response.status == 200:
                    self._creators_cache = await response.json(content_type=None)
                    logger.info(f"Syncing secret database...")
                    return self._creators_cache
        except Exception as e:
            logger.error(f"Error syncing database: {e}")
        
        return []

    async def find_all_matching_creators(self, model_name: str) -> List[Dict[str, Any]]:
        """Find all creators matching the search term"""
        creators = await self._get_creators_list()
        if not creators:
            return []
        
        import re
        search_normalized = re.sub(r'[\s_-]+', '', model_name.lower().strip())
        matches = []
        
        for creator in creators:
            name = creator.get('name', '').lower()
            name_normalized = re.sub(r'[\s_-]+', '', name)
            
            if (search_normalized == name_normalized or 
                search_normalized in name_normalized or
                name_normalized in search_normalized):
                matches.append(creator)
        
        matches.sort(key=lambda c: len(c.get('name', '')))
        return matches[:10]

    async def fetch_posts_paged(self, creator: Dict[str, Any], offset: int = 0) -> List[MediaItem]:
        """Fetch a single page of posts"""
        media_items = []
        service = creator.get('service')
        creator_id = creator.get('id')
        
        if not service or not creator_id:
            return media_items
        
        try:
            posts_url = f"{self.BASE_URL}/api/v1/{service}/user/{creator_id}/posts?o={offset}"
            async with self.session.get(posts_url) as response:
                if response.status != 200:
                    return media_items
                
                posts = await response.json(content_type=None)
                if not isinstance(posts, list):
                    return media_items
                
                for post in posts:
                    post_id = post.get('id')
                    file_info = post.get('file', {})
                    if file_info and file_info.get('path'):
                        path = file_info['path']
                        media_url = f"{self.BASE_URL}/data{path}"
                        filename = file_info.get('name') or f"{post_id}_main"
                        ext = path.lower().split('.')[-1] if '.' in path else ''
                        media_type = "video" if ext in ['mp4', 'm4v', 'mov', 'webm', 'avi'] else "photo"
                        media_items.append(MediaItem(media_url, filename, media_type, str(post_id)))
                    
                    for i, attachment in enumerate(post.get('attachments', [])):
                        if attachment.get('path'):
                            path = attachment['path']
                            media_url = f"{self.BASE_URL}/data{path}"
                            filename = attachment.get('name') or f"{post_id}_att{i}"
                            ext = path.lower().split('.')[-1] if '.' in path else ''
                            media_type = "video" if ext in ['mp4', 'm4v', 'mov', 'webm', 'avi'] else "photo"
                            media_items.append(MediaItem(media_url, filename, media_type, str(post_id)))
        except:
            pass
            
        return media_items

    async def download_media(self, item: MediaItem) -> bool:
        """Download media to local storage"""
        if not self.session:
            return False
            
        ext = item.url.split('.')[-1].split('?')[0]
        local_filename = f"{item.post_id}_{item.filename}"
        if not local_filename.endswith(f".{ext}"):
            local_filename += f".{ext}"
            
        local_path = os.path.join(DOWNLOAD_DIR, local_filename)
        
        try:
            async with self.session.get(item.url) as response:
                if response.status == 200:
                    content = await response.read()
                    if not content:
                        logger.warning(f"Downloaded empty content for {item.url}")
                        return False
                    async with aiofiles.open(local_path, mode='wb') as f:
                        await f.write(content)
                    # Verify file size is non-zero
                    try:
                        if os.path.getsize(local_path) == 0:
                            logger.warning(f"File written but size is zero: {local_path}")
                            return False
                    except Exception:
                        pass
                    item.local_path = local_path
                    return True
        except:
            pass
            
        return False
