# Tutorial: Como Vincular sua Conta PayPal ao Bot

Para receber pagamentos diretamente na sua conta PayPal, você precisa criar uma aplicação no portal de desenvolvedores do PayPal e obter suas credenciais.

## Passo 1: Criar uma Conta de Desenvolvedor
1. Acesse o [PayPal Developer Portal](https://developer.paypal.com/).
2. Faça login com sua conta comercial (Business) do PayPal.

## Passo 2: Criar um App e Obter Credenciais
1. No menu lateral, clique em **Apps & Credentials**.
2. Certifique-se de estar na aba **REST API apps**.
3. Clique em **Create App**.
4. Dê um nome ao seu app (ex: `TelegramMediaBot`).
5. Após criar, você verá o **Client ID** e o **Secret**.
    *   **Importante:** Existem duas abas: **Sandbox** (para testes) e **Live** (para receber dinheiro real). Comece com Sandbox para testar e depois mude para Live.

## Passo 3: Configurar as Variáveis de Ambiente
No seu painel do Railway (ou no arquivo `.env`), adicione as seguintes variáveis:

```env
PAYPAL_CLIENT_ID=seu_client_id_aqui
PAYPAL_CLIENT_SECRET=seu_secret_aqui
PAYPAL_MODE=live  # Use 'sandbox' para testes ou 'live' para produção
```

## Passo 4: Configurar Preços Regionais
O bot já vem configurado com uma lógica de preços sugerida para maximizar suas vendas:

| Plano | Brasil (BRL) | LATAM (USD) | Global (USD) |
| :--- | :--- | :--- | :--- |
| **Semanal** | R$ 15,00 | $3.00 | $5.00 |
| **Mensal** | R$ 45,00 | $9.00 | $14.00 |
| **Vitalício** | R$ 99,00 | $19.00 | $25.00 |

*Esses valores podem ser ajustados no arquivo `bot/users_db.py` na função `get_pricing`.*

## Passo 5: Webhooks (Opcional para Automação Total)
Para que o bot libere o acesso instantaneamente após o pagamento sem que o usuário precise clicar em nada, você deve configurar um Webhook no PayPal apontando para a URL do seu bot no Railway.
1. No seu App no PayPal Developer, vá em **Webhooks**.
2. Adicione a URL: `https://seu-app.up.railway.app/paypal_webhook`.
3. Selecione o evento: `Checkout order approved`.

---
**Dica de Admin:** Para se tornar administrador do bot, pegue seu ID do Telegram (use o bot @userinfobot) e coloque na variável `ADMIN_ID` no Railway.
