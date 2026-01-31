# Deploy no Railway

Este bot roda em **polling (getUpdates)** e também sobe um servidor HTTP (aiohttp) para receber webhooks de pagamento (**Stripe** / **PushinPay**).

## 1) Volume persistente (obrigatório)

Crie um Volume no Railway e **monte em `/data`**.

- O SQLite precisa ficar em `/data` para persistir entre deploys.
- DB padrão (recomendado): `/data/bot_data.db`.

## 2) Escala (evitar 409 Conflict)

**Defina réplicas = 1**.

O bot usa polling; se duas instâncias rodarem ao mesmo tempo o Telegram retorna:
> `409 Conflict: terminated by other getUpdates request`

Além da escala 1, o bot implementa um lock por arquivo em:
- `BOT_LOCK_PATH` (se setado) ou
- `/data/bot.lock` (padrão)

Se outra instância já estiver rodando, o processo encerra.

## 3) Variáveis de ambiente

### Essenciais
- `BOT_TOKEN` – token do bot Telegram
- `ADMIN_ID` – seu user_id do Telegram (inteiro)
- `DB_PATH` – **recomendado:** `/data/bot_data.db`
- `PUBLIC_URL` – URL pública do Railway para webhooks e redirects (ex.: `https://<app>.up.railway.app`)
- `TELEGRAM_MAX_UPLOAD_MB` – limite de upload por arquivo (ex.: `45`)

### Stripe
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID` (se o fluxo do seu Stripe depender disso)

### PushinPay (PIX)
- `PUSHINPAY_TOKEN`
- `PUSHINPAY_WEBHOOK_TOKEN`

### Admin / Test
- `ADMIN_GOD_MODE` (opcional) – define o estado inicial do admin no DB (0/1)
- `ADMIN_FORCE_VIP` (opcional) – força VIP sempre (0/1) (uso recomendado apenas para testes)

### Opcional
- `BOT_LOCK_PATH` – caminho do lock (padrão: `/data/bot.lock`)
- `PAGE_MEDIA_LIMIT` – limite de mídias enviadas por página (padrão: `120`)

## 4) Start command

O projeto está pronto para rodar com:

- `python run.py`

No Railway, use o Procfile já existente.

## 5) Webhooks de pagamento

O servidor HTTP interno escuta em `$PORT` (Railway injeta essa variável).

Garanta que seu provedor de pagamento está apontando para o endpoint correto (consulte `app/payments_*` e `run.py`).

## 6) Checklist de produção

- [ ] Volume montado em `/data`
- [ ] `DB_PATH=/data/bot_data.db`
- [ ] réplicas = 1
- [ ] `PUBLIC_URL` setado
- [ ] Stripe e/ou PushinPay com tokens e webhook secrets
- [ ] Logs sem spam (httpx/urllib3 em INFO)
- [ ] Testes locais executados (ver `TESTS.md`)
