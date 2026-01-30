# 📘 ADMIN COMMANDS MANUAL

Complete guide to all administrative commands available in the Telegram VIP Media Bot.

---

## 🔐 Admin Access

Only users with the `ADMIN_ID` (set in environment variables) can execute admin commands. All admin commands will return an error message if executed by non-admin users.

---

## 📋 Available Admin Commands

### Channel Configuration Commands

#### `/setvip <channel_id>`
**Description:** Sets the VIP channel ID where VIP content is stored.

**Usage:**
```
/setvip -1001234567890
```

**Parameters:**
- `channel_id` (required): The Telegram channel ID (must be negative integer, e.g., -1001234567890)

**Example:**
```
/setvip -1001234567890
```

---

#### `/setfreept <channel_id>`
**Description:** Sets the FREE Portuguese channel ID.

**Usage:**
```
/setfreept -1001234567890
```

**Parameters:**
- `channel_id` (required): The Telegram channel ID for Portuguese free content

---

#### `/setfreees <channel_id>`
**Description:** Sets the FREE Spanish channel ID.

**Usage:**
```
/setfreees -1001234567890
```

**Parameters:**
- `channel_id` (required): The Telegram channel ID for Spanish free content

---

#### `/setfreeen <channel_id>`
**Description:** Sets the FREE English channel ID.

**Usage:**
```
/setfreeen -1001234567890
```

**Parameters:**
- `channel_id` (required): The Telegram channel ID for English free content

---

### Subscription Link Commands

#### `/setsubbot_pt <link>`
**Description:** Sets the subscription bot link for Portuguese users.

**Usage:**
```
/setsubbot_pt https://t.me/YourBot
```

**Parameters:**
- `link` (required): The Telegram bot/channel link

---

#### `/setsubbot_es <link>`
**Description:** Sets the subscription bot link for Spanish users.

**Usage:**
```
/setsubbot_es https://t.me/YourBot
```

---

#### `/setsubbot_en <link>`
**Description:** Sets the subscription bot link for English users.

**Usage:**
```
/setsubbot_en https://t.me/YourBot
```

---

### Media Source Configuration

#### `/setsource <url1,url2,...>`
**Description:** Sets the media source URLs (comma-separated).

**Usage:**
```
/setsource https://coomer.party,https://kemono.party
```

**Parameters:**
- `url1,url2,...` (required): Comma-separated list of media source URLs

**Example:**
```
/setsource https://coomer.party,https://kemono.party,https://example.com
```

---

### Preview Configuration

#### `/setpreview <type>`
**Description:** Sets the preview type for free users.

**Usage:**
```
/setpreview blur
```

**Parameters:**
- `type` (required): One of the following:
  - `blur` - Applies Gaussian blur to preview images
  - `watermark` - Adds "VIP ONLY" watermark to preview images
  - `lowres` - Reduces image resolution/quality
  - `none` - No preview modification (shows full content)

**Example:**
```
/setpreview watermark
```

---

#### `/setpreviewlimit <number>`
**Description:** Sets the maximum number of previews a free user can view per day.

**Usage:**
```
/setpreviewlimit 3
```

**Parameters:**
- `number` (required): Integer representing the daily preview limit (default: 3)

**Example:**
```
/setpreviewlimit 5
```

---

### Language Configuration

#### `/setlang <lang>`
**Description:** Sets the default bot language.

**Usage:**
```
/setlang pt
```

**Parameters:**
- `lang` (required): Language code - one of:
  - `pt` - Portuguese
  - `es` - Spanish
  - `en` - English

**Example:**
```
/setlang en
```

---

### Statistics & Monitoring

#### `/stats`
**Description:** Displays comprehensive bot statistics including:
- VIP channel configuration
- Free channels (PT, ES, EN)
- Media sources count
- Preview type
- Preview limit
- Batch settings
- Auto-post interval

**Usage:**
```
/stats
```

**Output Example:**
```
📊 Bot Statistics:
• VIP Channel: -1001234567890
• Free Channels: PT: -100..., ES: -100..., EN: -100...
• Media Sources: 2
• Preview Type: blur
• Preview Limit: 3
• Max Batch: 10
• Auto-post Interval: 60s
```

---

### User Management Commands

#### `/addadmin <user_id>`
**Description:** Adds a user to the authorized users list (whitelist).

**Usage:**
```
/addadmin 123456789
```

**Parameters:**
- `user_id` (required): The Telegram user ID to authorize

**Example:**
```
/addadmin 987654321
```

**Note:** This command may require additional implementation in the Config class.

---

#### `/removeadmin <user_id>`
**Description:** Removes a user from the authorized users list.

**Usage:**
```
/removeadmin 123456789
```

**Parameters:**
- `user_id` (required): The Telegram user ID to remove from whitelist

**Note:** Cannot remove the main admin (ADMIN_ID).

---

#### `/listadmins`
**Description:** Lists all authorized users (whitelist).

**Usage:**
```
/listadmins
```

**Output Example:**
```
📋 Usuários Autorizados

• 123456789 ⭐ (Admin Principal)
• 987654321
• 555444333

Total: 3 usuário(s)
```

---

### System Commands

#### `/restart`
**Description:** Restarts the bot. The process manager (Railway/PM2) will automatically restart it.

**Usage:**
```
/restart
```

**Warning:** This will temporarily disconnect the bot. Use with caution.

---

#### `/help`
**Description:** Shows help message. For admins, displays admin-specific help.

**Usage:**
```
/help
```

---

## 🎮 God Mode (Built-in Admin Feature)

Admins have access to a special "God Mode" toggle via the main keyboard button:

**Button:** `⚡ MODO GOD: {status}`

**Functionality:**
- When enabled (🟢): Admin bypasses all restrictions (preview limits, VIP checks, etc.)
- When disabled (🔴): Admin operates as a normal user (useful for testing)

**Toggle:** Click the button in the main keyboard to toggle God Mode on/off.

---

## 🔍 Finding Channel IDs

To find a Telegram channel ID:

1. **For Public Channels:**
   - Use @userinfobot or @getidsbot
   - Forward a message from the channel to the bot

2. **For Private Channels:**
   - Add @userinfobot as admin to your channel
   - The bot will display the channel ID

3. **Via Telegram API:**
   - Use `getUpdates` method
   - Channel IDs are negative integers (e.g., -1001234567890)

---

## ⚠️ Important Notes

1. **Admin ID:** The `ADMIN_ID` is set via environment variable `ADMIN_ID` and cannot be changed via commands.

2. **Command Registration:** Some admin commands may need to be registered in `main.py` using `CommandHandler` to be active.

3. **Database Persistence:** Channel IDs and settings are stored in the SQLite database and persist across bot restarts.

4. **Error Handling:** All commands validate input and return error messages for invalid parameters.

5. **Logging:** All admin actions are logged for audit purposes.

---

## 🚀 Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `/setvip` | Set VIP channel | `/setvip -1001234567890` |
| `/setfreept` | Set PT free channel | `/setfreept -1001234567890` |
| `/setfreees` | Set ES free channel | `/setfreees -1001234567890` |
| `/setfreeen` | Set EN free channel | `/setfreeen -1001234567890` |
| `/setsubbot_pt` | Set PT subscription link | `/setsubbot_pt https://t.me/Bot` |
| `/setsubbot_es` | Set ES subscription link | `/setsubbot_es https://t.me/Bot` |
| `/setsubbot_en` | Set EN subscription link | `/setsubbot_en https://t.me/Bot` |
| `/setsource` | Set media sources | `/setsource url1,url2` |
| `/setpreview` | Set preview type | `/setpreview blur` |
| `/setpreviewlimit` | Set preview limit | `/setpreviewlimit 3` |
| `/setlang` | Set default language | `/setlang pt` |
| `/stats` | Show statistics | `/stats` |
| `/addadmin` | Add authorized user | `/addadmin 123456789` |
| `/removeadmin` | Remove authorized user | `/removeadmin 123456789` |
| `/listadmins` | List authorized users | `/listadmins` |
| `/restart` | Restart bot | `/restart` |
| `/help` | Show help | `/help` |

---

**Last Updated:** January 2026  
**Bot Version:** v8.3 Global Edition
