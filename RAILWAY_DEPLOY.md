# Guia de Deploy no Railway

Este bot foi otimizado para rodar no Railway com persistência de dados e entrega direta no PV.

## 1. Preparação do Repositório
1. Crie um novo repositório privado no seu GitHub.
2. Envie todos os arquivos da pasta `bot/` para este repositório.
3. Certifique-se de que o arquivo `requirements.txt` inclua as novas dependências:
   ```text
   python-telegram-bot
   requests
   rapidfuzz
   python-dotenv
   aiohttp
   aiofiles
   ```

## 2. Configuração no Railway
1. No [Railway](https://railway.app/), clique em **New Project** > **Deploy from GitHub repo**.
2. Selecione o repositório que você criou.
3. Vá em **Variables** e adicione as seguintes:

| Variável | Descrição |
| :--- | :--- |
| `BOT_TOKEN` | Token do seu bot obtido no @BotFather |
| `ADMIN_ID` | Seu ID do Telegram (para comandos de admin) |
| `PAYPAL_CLIENT_ID` | Obtido no portal do PayPal Developer |
| `PAYPAL_CLIENT_SECRET` | Obtido no portal do PayPal Developer |
| `PAYPAL_MODE` | `live` ou `sandbox` |
| `DATABASE_URL` | (Opcional) O bot usará SQLite por padrão se não houver |

## 3. Persistência de Dados (Volume)
Como o bot usa SQLite (`bot_data.db`), os dados seriam perdidos a cada novo deploy se não configurarmos um Volume:
1. No Railway, vá nas configurações do seu serviço.
2. Clique em **Volumes** > **Add Volume**.
3. Nomeie como `data` e monte no caminho `/home/ubuntu/bot_analysis/bot/` (ou onde o arquivo `.db` estiver sendo gerado).
4. Isso garante que as licenças dos seus usuários não sumam quando o bot reiniciar.

## 4. Comando de Inicialização
O Railway deve detectar automaticamente o `main_pv.py`, mas se necessário, configure o **Start Command**:
```bash
python bot/main_pv.py
```

## 5. Verificação
Após o deploy, envie `/start` para o seu bot. Se ele responder, está pronto para uso!
Use `/search` para testar a busca inteligente e o sistema de créditos.
