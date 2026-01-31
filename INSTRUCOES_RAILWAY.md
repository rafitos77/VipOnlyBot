# Instruções no Railway (resumo)

## Escala
- **Replicas = 1** (polling do Telegram não funciona com múltiplas instâncias).
- O bot usa lock em `/data/bot.lock` para evitar 2 instâncias ao mesmo tempo.

## Volume
- Monte um Volume em **`/data`**
- Use `DB_PATH=/data/bot_data.db`

## Variáveis essenciais
- `BOT_TOKEN`
- `ADMIN_ID`
- `PUBLIC_URL` (começa com `https://`, não use `.railway.internal`)

## Pagamentos
### Stripe (internacional)
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
Webhook: `POST {PUBLIC_URL}/webhooks/stripe`

### Asaas (PIX Brasil)
- `ASAAS_ACCESS_TOKEN`
- `ASAAS_WEBHOOK_TOKEN` (recomendado)
- `ASAAS_BASE_URL` (opcional, padrão: `https://api.asaas.com`)
Webhook: `POST {PUBLIC_URL}/webhooks/asaas?token={ASAAS_WEBHOOK_TOKEN}`

### NOWPayments (opcional / fallback cripto)
- `NOWPAYMENTS_API_KEY`
- `NOWPAYMENTS_IPN_SECRET`
Webhook: `POST {PUBLIC_URL}/webhooks/nowpayments`

## Healthcheck
- `GET {PUBLIC_URL}/healthz`
