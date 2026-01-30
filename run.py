import sys
import os
import logging

# Configuração de logs para o deploy
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Entrypoint")

# Adiciona o diretório atual ao sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logger.info(f"Iniciando bot a partir de: {BASE_DIR}")

try:
    # Importa o main de dentro do pacote 'app'
    from app.main import run_bot
    import asyncio
    
    if __name__ == "__main__":
        logger.info("Executando run_bot()...")
        asyncio.run(run_bot())
except ImportError as e:
    logger.critical(f"Erro de importação crítico: {e}")
    logger.info(f"Conteúdo do diretório atual: {os.listdir(BASE_DIR)}")
    if os.path.exists(os.path.join(BASE_DIR, 'app')):
        logger.info(f"Conteúdo da pasta 'app': {os.listdir(os.path.join(BASE_DIR, 'app'))}")
    sys.exit(1)
except Exception as e:
    logger.critical(f"Erro fatal na inicialização: {e}", exc_info=True)
    sys.exit(1)
