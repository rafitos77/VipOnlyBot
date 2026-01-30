# 🔧 ENVIRONMENT VARIABLES GUIDE

Complete reference guide for all environment variables used in the Telegram VIP Media Bot for Railway deployment.

---

## 📋 Table of Contents

1. [Required Variables](#required-variables)
2. [Payment Gateway Variables](#payment-gateway-variables)
3. [Optional Configuration Variables](#optional-configuration-variables)
4. [Railway-Specific Variables](#railway-specific-variables)
5. [Quick Setup Guide](#quick-setup-guide)

---

## ✅ Required Variables

These variables **MUST** be set for the bot to function.

### `BOT_TOKEN`
- **Description:** Your Telegram bot token obtained from [@BotFather](https://t.me/BotFather)
- **Type:** String
- **Required:** ✅ Yes
- **Example:** `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- **How to Get:**
  1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
  2. Send `/newbot` and follow the instructions
  3. Copy the token provided
- **Security:** ⚠️ Keep this secret! Never commit to version control.

---

### `ADMIN_ID`
- **Description:** Your Telegram user ID (used to grant admin privileges)
- **Type:** Integer
- **Required:** ✅ Yes
- **Example:** `123456789`
- **How to Get:**
  1. Send a message to [@userinfobot](https://t.me/userinfobot)
  2. It will reply with your user ID
  3. Copy the numeric ID
- **Note:** Only this user ID can execute admin commands

---

## 💳 Payment Gateway Variables

### Stripe (Telegram Native Payments)

#### `STRIPE_API_TOKEN`
- **Description:** Stripe secret API key for Telegram Native Payments (used for international/USD payments)
- **Type:** String
- **Required:** ✅ Yes (if accepting USD payments)
- **Example:** `sk_live_51AbCdEfGhIjKlMnOpQrStUvWxYz1234567890`
- **How to Get:**
  1. Sign up at [stripe.com](https://stripe.com)
  2. Go to Dashboard > Developers > API Keys
  3. Copy the "Secret key" (starts with `sk_live_` for production or `sk_test_` for testing)
- **Security:** ⚠️ Keep this secret! This is a sensitive credential.
- **Usage:** Used for Telegram's native payment system for USD transactions

---

### Pushin Pay (Pix Payments - Brazil)

#### `PUSHINPAY_API_KEY`
- **Description:** Pushin Pay API key for creating Pix charges
- **Type:** String
- **Required:** ✅ Yes (if accepting BRL/Pix payments)
- **Example:** `pk_live_abc123def456ghi789`
- **How to Get:**
  1. Sign up at [pushinpay.com](https://pushinpay.com) (or their API portal)
  2. Navigate to API Settings
  3. Copy your API key
- **Security:** ⚠️ Keep this secret!
- **Usage:** Used to create Pix payment charges for Brazilian users

---

#### `PUSHINPAY_WEBHOOK_SECRET`
- **Description:** Secret key for verifying webhook signatures from Pushin Pay
- **Type:** String
- **Required:** ✅ Yes (if using Pushin Pay)
- **Example:** `whsec_1234567890abcdef`
- **How to Get:**
  1. In Pushin Pay dashboard, go to Webhooks section
  2. Generate or copy the webhook secret
  3. This is used to verify incoming webhook requests are legitimate
- **Security:** ⚠️ Keep this secret! Used for webhook security.

---

#### `WEBHOOK_URL`
- **Description:** Public URL where Pushin Pay will send webhook notifications
- **Type:** String (URL)
- **Required:** ✅ Yes (if using Pushin Pay)
- **Example:** `https://your-bot-name.railway.app`
- **How to Get:**
  1. Deploy your bot on Railway
  2. Railway provides a public URL (e.g., `https://your-service-name.railway.app`)
  3. Use this URL (no trailing slash)
- **Note:** This must be publicly accessible. Railway provides HTTPS automatically.

---

#### `WEBHOOK_PORT`
- **Description:** Port number for the webhook server to listen on
- **Type:** Integer
- **Required:** ❌ No (default: `8080`)
- **Example:** `8080`
- **Default:** `8080`
- **Note:** Railway automatically maps ports. Usually `8080` or `PORT` environment variable.

---

## 🔧 Optional Configuration Variables

### Channel Configuration

#### `VIP_CHANNEL_ID`
- **Description:** Telegram channel ID where VIP content is stored
- **Type:** Integer (negative)
- **Required:** ❌ No
- **Example:** `-1001234567890`
- **How to Get:** Use [@userinfobot](https://t.me/userinfobot) or forward a message from the channel
- **Note:** Can also be set via `/setvip` admin command

---

#### `FREE_CHANNEL_PT_ID`
- **Description:** Free content channel ID for Portuguese users
- **Type:** Integer (negative)
- **Required:** ❌ No
- **Example:** `-1001234567890`

---

#### `FREE_CHANNEL_ES_ID`
- **Description:** Free content channel ID for Spanish users
- **Type:** Integer (negative)
- **Required:** ❌ No
- **Example:** `-1001234567890`

---

#### `FREE_CHANNEL_EN_ID`
- **Description:** Free content channel ID for English users
- **Type:** Integer (negative)
- **Required:** ❌ No
- **Example:** `-1001234567890`

---

### Subscription Links

#### `SUB_LINK_PT`
- **Description:** Subscription bot/channel link for Portuguese users
- **Type:** String (URL)
- **Required:** ❌ No
- **Example:** `https://t.me/YourBot`
- **Default:** `https://t.me/YourBot`

---

#### `SUB_LINK_ES`
- **Description:** Subscription bot/channel link for Spanish users
- **Type:** String (URL)
- **Required:** ❌ No
- **Example:** `https://t.me/YourBot`
- **Default:** `https://t.me/YourBot`

---

#### `SUB_LINK_EN`
- **Description:** Subscription bot/channel link for English users
- **Type:** String (URL)
- **Required:** ❌ No
- **Example:** `https://t.me/YourBot`
- **Default:** `https://t.me/YourBot`

---

### Performance Settings

#### `MAX_FILES_PER_BATCH`
- **Description:** Maximum number of files to process in a single batch
- **Type:** Integer
- **Required:** ❌ No
- **Example:** `10`
- **Default:** `10`
- **Note:** Higher values may cause rate limiting issues

---

## 🚂 Railway-Specific Variables

### `RAILWAY_VOLUME_MOUNT_PATH`
- **Description:** Path where Railway volume is mounted (for persistent database storage)
- **Type:** String (path)
- **Required:** ❌ No
- **Example:** `/data`
- **How to Set:**
  1. In Railway dashboard, go to your service
  2. Go to Settings > Volumes
  3. Create a volume and mount it to `/data`
  4. Railway automatically sets this variable
- **Note:** If not set, database will be stored in the project root (may be lost on redeploy)

---

### `PORT`
- **Description:** Port number Railway assigns (usually automatic)
- **Type:** Integer
- **Required:** ❌ No (Railway sets automatically)
- **Example:** `8080`
- **Note:** Railway sets this automatically. Don't override unless necessary.

---

## 🚀 Quick Setup Guide

### Minimum Required Setup

For basic bot functionality:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
```

### With Stripe (USD Payments)

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
STRIPE_API_TOKEN=sk_live_your_stripe_key
```

### With Pushin Pay (Pix/BRL Payments)

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
PUSHINPAY_API_KEY=your_pushinpay_api_key
PUSHINPAY_WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_URL=https://your-bot.railway.app
WEBHOOK_PORT=8080
```

### Complete Setup (Both Payment Gateways)

```env
# Required
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id

# Stripe (USD)
STRIPE_API_TOKEN=sk_live_your_stripe_key

# Pushin Pay (Pix/BRL)
PUSHINPAY_API_KEY=your_pushinpay_api_key
PUSHINPAY_WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_URL=https://your-bot.railway.app
WEBHOOK_PORT=8080

# Optional
VIP_CHANNEL_ID=-1001234567890
MAX_FILES_PER_BATCH=10
RAILWAY_VOLUME_MOUNT_PATH=/data
```

---

## 📝 Setting Variables in Railway

1. **Via Railway Dashboard:**
   - Go to your service
   - Click on "Variables" tab
   - Click "New Variable"
   - Enter variable name and value
   - Click "Add"

2. **Via Railway CLI:**
   ```bash
   railway variables set BOT_TOKEN=your_token_here
   railway variables set ADMIN_ID=123456789
   ```

3. **Via `railway.toml` (if using):**
   ```toml
   [build]
   [deploy]
   [deploy.variables]
   BOT_TOKEN = "your_token_here"
   ADMIN_ID = "123456789"
   ```

---

## 🔒 Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use Railway's Variables** instead of hardcoding secrets
3. **Rotate API keys** periodically
4. **Use test keys** during development (`sk_test_` for Stripe)
5. **Verify webhook signatures** (automatically handled by the bot)
6. **Limit admin access** to trusted users only

---

## ✅ Validation

The bot validates required variables on startup. If validation fails, the bot will:
- Log a critical error
- Exit with error code
- Display which variables are missing

Check logs in Railway dashboard if the bot fails to start.

---

## 🆘 Troubleshooting

### Bot won't start
- ✅ Check `BOT_TOKEN` is correct
- ✅ Check `ADMIN_ID` is a valid integer
- ✅ Check Railway logs for specific error messages

### Payments not working
- ✅ Verify `STRIPE_API_TOKEN` is correct (for USD)
- ✅ Verify `PUSHINPAY_API_KEY` and `PUSHINPAY_WEBHOOK_SECRET` (for Pix)
- ✅ Check `WEBHOOK_URL` is publicly accessible
- ✅ Verify webhook is registered in Pushin Pay dashboard

### Database not persisting
- ✅ Set up Railway volume and mount to `/data`
- ✅ Verify `RAILWAY_VOLUME_MOUNT_PATH` is set (automatic if volume mounted)

---

## 📚 Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Pushin Pay Documentation](https://docs.pushinpay.com) (check their official docs)
- [Railway Documentation](https://docs.railway.app)

---

**Last Updated:** January 2026  
**Bot Version:** v8.3 Global Edition
