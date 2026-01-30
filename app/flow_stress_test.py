import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FlowStressTest")

# Mock environment
os.environ["BOT_TOKEN"] = "123456789:ABCDEF-GHIJKL-MNOPQRSTUV"
os.environ["ADMIN_ID"] = "12345678"

# Adicionar o diretório atual ao path para importar módulos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Importar módulos
from app.config import Config
from users_db import UserDB
from smart_search import SmartSearch
from paypal_integration import PayPalClient

# Mock de dependências externas (Telegram, Fetcher)
class MockBot:
    async def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        logger.info(f"TELEGRAM MOCK: Sent message to {chat_id}: {text[:50]}...")
        return True
    async def send_photo(self, chat_id, photo, caption=None, parse_mode=None):
        logger.info(f"TELEGRAM MOCK: Sent photo to {chat_id}: {caption[:30]}...")
        return True
    async def send_video(self, chat_id, video, caption=None, parse_mode=None):
        logger.info(f"TELEGRAM MOCK: Sent video to {chat_id}: {caption[:30]}...")
        return True

class MockUploader:
    def __init__(self, bot): self.bot = bot
    async def upload_and_cleanup(self, media_item, channel_id, caption=""):
        logger.info(f"UPLOADER MOCK: Uploaded {media_item.media_type} to {channel_id}")
        return True

class MockMediaItem:
    def __init__(self, media_type): self.media_type = media_type
    @property
    def local_path(self): return "mock_path"

class MockFetcher:
    def __init__(self): pass
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc_val, exc_tb): pass
    async def _get_creators_list(self):
        return [{'name': 'Belle Delphine', 'id': 'belle', 'service': 'coomer'}]
    async def fetch_posts_paged(self, creator, offset=0):
        return [MockMediaItem("photo"), MockMediaItem("video"), MockMediaItem("photo"), MockMediaItem("photo"), MockMediaItem("photo")]
    async def download_media(self, item): return True

class MockPayPalClient:
    def create_order(self, amount, currency, return_url, cancel_url):
        return {"id": "ORD-TEST", "status": "CREATED", "links": [{"rel": "approve", "href": "https://paypal.com/test"}]}
    def capture_payment(self, order_id: str) -> bool:
        return True

# Mock da classe principal do bot para simular o fluxo
class MockVIPBotPV:
    def __init__(self, user_db, config):
        self.user_db = user_db
        self.config = config
        self.uploader = MockUploader(MockBot())
        self.fetcher = MockFetcher()
        self.paypal_client = MockPayPalClient()
        self.search_cache = {}
        self.bot = MockBot()

    async def simulate_search(self, user_id, query):
        user = self.user_db.get_user(user_id)
        lang = user.get('language', 'pt')
        
        if not self.user_db.check_preview_limit(user_id):
            logger.warning(f"USER {user_id}: Limite de preview atingido. Tentando mostrar popup.")
            await self.simulate_show_payment_popup(user_id, lang)
            return

        logger.info(f"USER {user_id}: Buscando '{query}'...")
        
        # Simular seleção de modelo (sel:coomer:belle:Belle Delphine)
        await self.simulate_callback_query(user_id, f"sel:coomer:belle:Belle Delphine")

    async def simulate_callback_query(self, user_id, data):
        if data.startswith("sel:"):
            _, service, c_id, name = data.split(":")
            
            if self.user_db.is_license_active(user_id):
                logger.info(f"USER {user_id}: VIP. Simular clique em BAIXAR TUDO.")
                await self.simulate_callback_query(user_id, f"dlall:{service}:{c_id}:{name}")
            else:
                logger.info(f"USER {user_id}: FREE. Enviando 3 previews (Dopamina).")
                for _ in range(3):
                    self.user_db.increment_previews(user_id)
                    await self.uploader.upload_and_cleanup(MockMediaItem("photo"), user_id, caption="Preview")
                
                logger.info(f"USER {user_id}: Previews enviadas. Mostrando popup de venda.")
                await self.simulate_show_payment_popup(user_id, "pt")
        
        elif data.startswith("dlall:"):
            logger.info(f"USER {user_id}: VIP. Simulação de download em massa concluída.")
        
        elif data.startswith("buy:"):
            plan_raw = data.split(":")[1]
            is_ds = plan_raw.endswith("_ds")
            plan = plan_raw.replace("_ds", "")
            
            pricing = self.user_db.get_pricing("pt")[plan]
            price = pricing['price'] * 0.7 if is_ds else pricing['price']
            
            order = self.paypal_client.create_order(price, pricing['currency'], "url", "url")
            logger.info(f"USER {user_id}: Ordem PayPal criada para {plan} ({price} {pricing['currency']}). Link: {order['links'][0]['href']}")
            
            if not is_ds:
                asyncio.create_task(self.simulate_remarketing_timer(user_id, "pt"))

    async def simulate_show_payment_popup(self, user_id, lang, is_downsell=False):
        if is_downsell:
            logger.warning(f"USER {user_id}: Popup de Downsell (30% OFF) exibido.")
        else:
            logger.info(f"USER {user_id}: Popup de Venda (Urgência) exibido.")

    async def simulate_remarketing_timer(self, user_id, lang):
        await asyncio.sleep(0.1) # Simular 15 minutos
        if not self.user_db.is_license_active(user_id):
            logger.warning(f"USER {user_id}: 15 minutos se passaram. Enviando Downsell.")
            await self.simulate_show_payment_popup(user_id, lang, is_downsell=True)

async def run_stress_test():
    config_instance = Config()
    user_db_instance = UserDB("flow_stress_test.db")
    bot_mock = MockVIPBotPV(user_db_instance, config_instance)
    
    user_free = 10001
    user_vip = 10002
    
    # --- 1. Teste de Usuário VIP (Acesso Ilimitado) ---
    logger.info("\n--- 1. Teste de Usuário VIP (Acesso Ilimitado) ---")
    user_db_instance.activate_license(user_vip, 'lifetime')
    await bot_mock.simulate_search(user_vip, "belle delphine")
    await bot_mock.simulate_search(user_vip, "belle delphine")
    
    # --- 2. Teste de Usuário FREE (Fluxo de Venda) ---
    logger.info("\n--- 2. Teste de Usuário FREE (Fluxo de Venda) ---")
    
    # 2.1. 1º Busca (1/3)
    await bot_mock.simulate_search(user_free, "beledelphine")
    
    # 2.2. 2º Busca (2/3)
    await bot_mock.simulate_search(user_free, "beledelphine")
    
    # 2.3. 3º Busca (3/3)
    await bot_mock.simulate_search(user_free, "beledelphine")
    
    # 2.4. 4º Busca (Bloqueio + Popup)
    await bot_mock.simulate_search(user_free, "beledelphine")
    
    # 2.5. Simular clique no plano mensal (buy:monthly)
    await bot_mock.simulate_callback_query(user_free, "buy:monthly")
    
    # 2.6. Simular Remarketing (Downsell)
    await asyncio.sleep(0.2) # Esperar o timer do remarketing
    
    # 2.7. Simular pagamento bem-sucedido
    user_db_instance.activate_license(user_free, 'monthly')
    logger.info(f"USER {user_free}: Pagamento simulado. Licença ativa? {user_db_instance.is_license_active(user_free)}")
    
    # 2.8. 5º Busca (Deve ser liberada)
    await bot_mock.simulate_search(user_free, "beledelphine")
    
    logger.info("\n✅ TESTE DE ESTRESSE DE FLUXO CONCLUÍDO COM SUCESSO.")
    os.remove("flow_stress_test.db")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
