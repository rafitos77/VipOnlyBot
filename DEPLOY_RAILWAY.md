# Deploy no Railway

Este bot roda em **polling (getUpdates)** e também sobe um servidor HTTP interno para receber **webhooks de pagamento**.

Gateways suportados neste build:
- **Stripe** (internacional – EN/ES)
- **Asaas (PIX)** (Brasil – PT/BRL)
- **NOWPayments (Cripto)** *(opcional)*: fallback internacional quando o Stripe retornar erro de “payment methods” indisponíveis.

---

## 1) Volume persistente (obrigatório)

Crie um Volume no Railway e **monte em `/data`**.

- O SQLite precisa ficar em `/data` para persistir entre deploys.
- DB padrão (recomendado): `/data/bot_data.db`.
- O lock de instância também fica em `/data/bot.lock`.

---

## 2) Escala (evitar 409 Conflict)

**Defina réplicas = 1**.

O bot usa polling; se duas instâncias rodarem ao mesmo tempo o Telegram retorna:

`Conflict: terminated by other getUpdates request`

✅ Além disso, este build implementa **file-lock** em `/data/bot.lock`: se outra instância já estiver rodando, o processo encerra.

---

## 3) Variáveis de ambiente

### Essenciais
- `BOT_TOKEN` – token do bot Telegram
- `ADMIN_ID` – seu user_id do Telegram (inteiro)
- `DB_PATH` – **recomendado:** `/data/bot_data.db`
- `PUBLIC_URL` – URL pública do Railway para webhooks e redirects  
  Ex.: `https://<app>.up.railway.app`  
  ⚠️ **Precisa começar com `https://`** (não use `.railway.internal`)
- `TELEGRAM_MAX_UPLOAD_MB` – limite de upload por arquivo (ex.: `45`)

### Stripe (internacional)
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID` (se existir no seu fluxo)

**Webhook Stripe:** `POST {PUBLIC_URL}/webhooks/stripe`

Eventos recomendados:
- `checkout.session.completed`
- (se usar assinatura) `invoice.paid`, `customer.subscription.updated`

### Asaas (PIX Brasil)
- `ASAAS_ACCESS_TOKEN`
- `ASAAS_WEBHOOK_TOKEN` *(opcional mas recomendado)* – token simples para validar chamadas no endpoint do webhook
- `ASAAS_PIX_LINK_WEEKLY` – link de pagamento PIX (plano semanal)
- `ASAAS_PIX_LINK_MONTHLY` – link de pagamento PIX (plano mensal)
- `ASAAS_PIX_LINK_LIFETIME` – link de pagamento PIX (plano vitalício)
- `ASAAS_BASE_URL` *(opcional)* – default `https://api.asaas.com`  
  (para sandbox, use o host sandbox do Asaas)

**Modo PIX (A2 / link de pagamento):** o bot envia um link do Asaas e pede o *ID do pagamento* (`pay_...`) para confirmar.

**Webhook Asaas:** `POST {PUBLIC_URL}/webhooks/asaas?token={ASAAS_WEBHOOK_TOKEN}`  
(Se você definir `ASAAS_WEBHOOK_TOKEN`, o bot exige o token via query string ou header)

Eventos suportados:
- `PAYMENT_RECEIVED`
- `PAYMENT_CONFIRMED`

### Cripto (NOWPayments) – opcional (fallback)
- `NOWPAYMENTS_API_KEY`
- `NOWPAYMENTS_IPN_SECRET`
- `NOWPAYMENTS_PAY_CURRENCY` *(recomendado)* – moeda que o cliente vai pagar (ex.: `xmr`, `usdttrc20`, `btc`). Default: `xmr`.
- `NOWPAYMENTS_BASE_URL` *(opcional)* – default `https://api.nowpayments.io`

**Webhook NOWPayments (IPN):** `POST {PUBLIC_URL}/webhooks/nowpayments`

---

## 4) Configurando os webhooks no painel

### Stripe
1. Stripe Dashboard → Developers → Webhooks
2. **Add endpoint** → cole `{PUBLIC_URL}/webhooks/stripe`
3. Selecione os eventos recomendados e salve.
4. Copie o **Signing secret** do endpoint e coloque em `STRIPE_WEBHOOK_SECRET`.

> Dica: o botão de “Send test webhook” aparece na página do endpoint (modo *test* ajuda).  
> No Railway não existe “Shell” nativo — para testar com CLI, rode o `stripe` CLI **no seu PC**.

### Asaas
1. Asaas → Integrações/Notificações (Webhooks)
2. Endpoint: `{PUBLIC_URL}/webhooks/asaas?token={ASAAS_WEBHOOK_TOKEN}`
3. Selecione eventos de pagamento confirmado/recebido e salve.

### NOWPayments
1. NOWPayments → IPN settings
2. IPN callback URL: `{PUBLIC_URL}/webhooks/nowpayments`
3. Defina o IPN Secret e replique em `NOWPAYMENTS_IPN_SECRET`.

---

## 5) Healthcheck

- `GET {PUBLIC_URL}/healthz` deve retornar algo como `OK true`.

---

## 6) Troubleshooting rápido

### “Invalid URL: An explicit scheme (https) must be provided”
- Seu `PUBLIC_URL` está sem `https://` ou você usou um domínio interno (`.railway.internal`).

### Stripe: “No valid payment method types for this Checkout Session”
- Isso acontece quando sua conta não tem métodos compatíveis ativados (ex.: verificação pendente).
- O bot mantém Stripe ativo, mas pode oferecer fallback cripto se `NOWPAYMENTS_API_KEY` estiver configurado.

### Erros em UI (BadRequest no editMessageText)
- Este build já usa `safe_edit_or_send()` e handler global para não derrubar os fluxos.


## NOWPayments

- NOWPAYMENTS_API_KEY
- NOWPAYMENTS_IPN_SECRET
- NOWPAYMENTS_PAY_CURRENCY (ex: usdttrc20)
- NOWPAYMENTS_DISABLED_PLANS (opcional, ex: weekly,weekly_ds) - desativa cripto para planos específicos
