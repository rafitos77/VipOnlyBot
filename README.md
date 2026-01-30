# 🚀 Bot VIP Telegram - Versão Zero Erro (v4.9)

Este pacote foi reestruturado para garantir um deploy automático e sem erros no Railway.

## 🛠️ Como fazer o Deploy (Rápido)

1.  **GitHub**: Crie um repositório privado e suba **todos** os arquivos deste pacote diretamente na raiz (não coloque dentro de uma pasta `bot/`).
2.  **Railway**:
    *   Conecte seu repositório.
    *   O Railway detectará o `requirements.txt` e o `main.py` automaticamente.
3.  **Variáveis de Ambiente**: Adicione as seguintes variáveis no painel do Railway:
    *   `BOT_TOKEN`: Token do @BotFather.
    *   `ADMIN_ID`: Seu ID do Telegram.
    *   `PAYPAL_CLIENT_ID`: Seu Client ID do PayPal.
    *   `PAYPAL_CLIENT_SECRET`: Seu Secret do PayPal.
    *   `PAYPAL_MODE`: `live` ou `sandbox`.

## 📂 Estrutura de Arquivos
*   `main.py`: Arquivo principal (antigo `main_pv.py`).
*   `requirements.txt`: Dependências auditadas.
*   `users_db.py`: Banco de dados com suporte a volumes.
*   `ADMIN_MEGA_TUTORIAL.md`: Guia completo de comandos e estratégias.

## 🛡️ Persistência de Dados
Para não perder as licenças dos usuários, adicione um **Volume** no Railway montado em `/data`. O bot detectará automaticamente e salvará o banco de dados lá.
