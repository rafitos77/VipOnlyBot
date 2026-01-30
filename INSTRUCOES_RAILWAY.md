# Deploy no Railway (VIP Media Bot)

O bot roda em polling (Telegram) e também sobe um servidor HTTP (aiohttp) no `PORT` do Railway para receber webhooks de pagamento e liberar VIP automaticamente.

## 1) Variáveis de ambiente

Obrigatórias:
- `BOT_TOKEN`
- `ADMIN_ID`
- `VIP_CHANNEL_ID`

Recomendadas (para webhooks funcionarem):
- `PUBLIC_URL`  (URL pública do serviço no Railway, ex: `https://seu-app.up.railway.app`)

Stripe (internacional):
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

PushinPay (Brasil/PIX):
- `PUSHINPAY_TOKEN`
- `PUSHINPAY_WEBHOOK_TOKEN` (opcional, mas recomendado: protege o endpoint do webhook)
- `PUSHINPAY_BASE_URL` (opcional, padrão: `https://api.pushinpay.com.br`)

## 2) Webhooks

### Stripe
Crie um endpoint no painel da Stripe apontando para:
- `{PUBLIC_URL}/webhooks/stripe`

Copie o Signing secret do endpoint e coloque em `STRIPE_WEBHOOK_SECRET`.

### PushinPay
Configure o webhook para:
- `{PUBLIC_URL}/webhooks/pushinpay?token={PUSHINPAY_WEBHOOK_TOKEN}`

Se você não usar token, deixe `PUSHINPAY_WEBHOOK_TOKEN` vazio e use:
- `{PUBLIC_URL}/webhooks/pushinpay`

## 3) Persistência de dados (não perder VIPs)
Adicione um Volume no Railway montado em `/data`. O SQLite será salvo em `/data/bot_data.db`.

## 4) Como testar
1. Deploy no Railway
2. Envie `/start` para o bot
3. Faça uma busca e tente comprar um plano
4. Após pagar, o bot deve enviar “Pagamento confirmado! VIP ativado.”
