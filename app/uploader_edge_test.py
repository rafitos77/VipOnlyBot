import os
import sys
import asyncio
from types import SimpleNamespace

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.uploader import TelegramUploader
except ModuleNotFoundError as e:
    # Offline test environments may not have python-telegram-bot installed.
    print("SKIPPED uploader_edge_test: telegram module not available")
    sys.exit(0)

from app.fetcher import MediaItem

class DummyBot:
    async def send_photo(self, chat_id, photo, caption=None, parse_mode=None, reply_markup=None):
        return SimpleNamespace(message_id=1)

    async def send_video(self, chat_id, video, caption=None, parse_mode=None, reply_markup=None):
        return SimpleNamespace(message_id=2)

    async def send_media_group(self, chat_id, media):
        # Return list of messages matching length
        return [SimpleNamespace(message_id=10+i) for i in range(len(media))]

async def main():
    os.environ.setdefault('TELEGRAM_MAX_UPLOAD_MB', '1')  # 1MB limit for test
    uploader = TelegramUploader(DummyBot())

    tmp_dir = '/tmp/uploader_edge'
    os.makedirs(tmp_dir, exist_ok=True)

    empty_path = os.path.join(tmp_dir, 'empty.mp4')
    open(empty_path, 'wb').close()

    big_path = os.path.join(tmp_dir, 'big.mp4')
    with open(big_path, 'wb') as f:
        f.write(b'0' * (2 * 1024 * 1024))  # 2MB

    ok_path = os.path.join(tmp_dir, 'ok.jpg')
    with open(ok_path, 'wb') as f:
        f.write(b'1' * 100)

    items = []
    for p, t in [(empty_path, 'video'), (big_path, 'video'), (ok_path, 'photo')]:
        it = MediaItem('file://local', os.path.basename(p), media_type=t, post_id='t')
        it.local_path = p
        items.append(it)

    # Single should skip empty and oversized, succeed on ok
    assert await uploader.upload_and_cleanup(items[0], 123, caption='x') is False
    assert await uploader.upload_and_cleanup(items[1], 123, caption='x') is False
    assert await uploader.upload_and_cleanup(items[2], 123, caption='x') is True

    # Group should skip empty and oversized and send only ok
    # Recreate ok file because previous cleanup removed it
    with open(ok_path, 'wb') as f:
        f.write(b'1' * 100)
    items[2].local_path = ok_path

    ids = await uploader._upload_batch(123, items, caption='cap')
    assert len(ids) == 1

    print('EDGE TEST PASSED')

if __name__ == '__main__':
    asyncio.run(main())
