# Bot functionalities – fetch, upload, search, invite, user interaction

Overview of how the bot implements **download (fetch)**, **upload**, **user interaction**, **invite (referral)**, **search**, and related flows.

---

## 1. Search

**Where:** `app/main.py` (handle_message), `app/smart_search.py`, `app/fetcher.py`

**Flow:**
1. User taps **🔍 Buscar Modelo** (or sends any text when not in a special state).
2. Bot sets `context.user_data['state'] = 'searching'` and sends `search_prompt` (PT/ES/EN).
3. User sends a model name (e.g. `belle delphine`).
4. Bot calls `MediaFetcher()._get_creators_list()` (Coomer.st API) and `smart_search.find_similar(query, creators)`.
5. **Smart search** (RapidFuzz, `token_sort_ratio`, score ≥ 60): returns up to 8 matches; handles typos and word order (“delphine belle” ↔ “belle delphine”).
6. Bot shows up to 8 buttons: each label = creator name, `callback_data = "sel:{service}:{id}:{name[:20]}"`.
7. `context.user_data['state']` is cleared after showing results.

**Behaviour:**
- No matches → `no_media_found` (by name).
- API/network error → `error_occurred` with “Timeout”.
- All copy is localized (PT/ES/EN) via `get_text(..., lang)`.

---

## 2. Fetch (download)

**Where:** `app/fetcher.py` – `MediaFetcher`

**Used when:**
- After user selects a creator (**sel:**).
- When user chooses **BAIXAR TUDO** or **Ver Primeira Página** (**dlall:** / **dlpage:**).
- On `/start` for the “visual welcome” (random creator from a fixed list).

**Mechanics:**
- **Creators list:** `GET {BASE_URL}/api/v1/creators` (cached in `_creators_cache` for the session).
- **Posts for a creator:** `GET {BASE_URL}/api/v1/{service}/user/{creator_id}/posts?o={offset}`.
- Each post → `MediaItem`(url, filename, media_type, post_id). Main file + attachments; `media_type` = photo or video from extension.
- **Download:** `download_media(item)` – GET item URL, save under `downloads/{post_id}_{filename}.{ext}`, set `item.local_path`. Uses `aiohttp` + `aiofiles`, 180s timeout.

**Limits:**
- **Preview path (sel:):** up to 3 items (first 3 posts).
- **Full download (dlall/dlpage):** up to 50 items, in batches of 10, with 1.2s delay per item and 2s between batches.

**Cleanup:** After each upload, `uploader.upload_and_cleanup()` deletes the local file.

---

## 3. Upload

**Where:** `app/uploader.py` – `TelegramUploader`

**Main entry for user-facing media:** `upload_and_cleanup(media_item, channel_id, caption)`.

- **channel_id** is the **user’s chat_id** (not a channel): media is sent in private chat.
- Sends photo or video with caption (Markdown).
- Deletes `media_item.local_path` after send.
- If `channel_id == config.VIP_CHANNEL_ID`, the message_id is stored in `vip_message_ids` (for optional “preview from VIP” flow; not used in the current main flow for previews).

**Other methods:**
- `_upload_single`, `_upload_batch`: single photo/video or media group.
- `_send_with_retry`: retries on `RetryAfter` and `TimedOut` (Telegram rate limits / timeouts).
- `upload_to_vip`, `send_previews_from_vip`: for uploading/forwarding to VIP and FREE channels (used when VIP/FREE channel IDs and flow are configured).

**Where upload is used in main flow:**
- **Previews (free user, sel:):** for each of the first 3 items: `fetcher.download_media(item)` → `uploader.upload_and_cleanup(item, user_id, caption="🔥 Preview: {name}")`.
- **VIP download (dlall/dlpage):** for each item: same download → `upload_and_cleanup(..., caption="✅ {name} - VIP")`.
- **Welcome:** one random media from a “big three” creator → `upload_and_cleanup(..., caption=welcome_title + welcome_copy, reply_markup=main_keyboard)`.

So: **fetch** = download from Coomer.st to disk; **upload** = send that file to the user in Telegram and then delete the file.

---

## 4. User interaction (keyboard, buttons, states)

**Where:** `app/main.py` – `get_main_keyboard`, `handle_message`, `on_callback_query`

**Main keyboard (reply):**
- Rows: [Buscar Modelo | Acesso VIP Total], [Ganhar Mídias Grátis | Minha Conta], [Idioma | Ajuda].
- If admin: extra row **⚡ MODO GOD: {status}** (toggles God Mode).

**Text handlers (handle_message):**
- **Buscar Modelo** → search prompt, set state `searching`.
- **Acesso VIP Total** → `show_payment_popup(..., is_downsell=False)`.
- **Ganhar Mídias Grátis** → referral message with link and stats (see Invite).
- **Minha Conta** → status (VIP/FREE), créditos, convidados.
- **Idioma** → language choice (PT/ES/EN) inline buttons.
- **Ajuda** → `welcome_copy`.
- **⚡ MODO GOD** (admin only) → toggle `is_god_mode`, refresh keyboard.
- If state is `searching` or text is not command and not “⚡ …” → treat as **search query** (search flow above).

**Callback handlers (on_callback_query):**
- **setlang:pt|es|en** → save language, delete message, call `cmd_start` (welcome again with main keyboard).
- **sel:service:id:name** → load creator, fetch first page; then either show “Download all / View page” (VIP or credit) or send 3 previews + payment popup (free, within preview limit), or only payment popup (preview limit exceeded).
- **dlall:...** / **dlpage:...** → fetch (with offset for dlpage) and upload up to 50 items to the user.
- **buy:plan** / **buy:plan_ds** → Stripe invoice (USD) or Pushin Pay Pix (BRL); plan and downsell flag from callback_data.
- **check_pix:id** → check Pix payment status and, if paid, activate license and confirm.

So: **user interaction** = main menu, search state, language, VIP/payment popup, download/preview buttons, and payment confirmation – all driven by reply keyboard + inline callbacks.

---

## 5. Invite (referral)

**Where:** `app/main.py` (cmd_start, handle_message), `app/users_db.py` (`process_referral`)

**Link format:** `https://t.me/{bot_username}?start=ref{user_id}`.

**When user opens the ref link:**
- `cmd_start` with `context.args = ['ref123456']`.
- `process_referral(new_user_id, referrer_id)`:
  - New user is created/get; if not already `referred_by`, set `referred_by = referrer_id`.
  - Referrer: `referral_count += 1`, `credits += 3`.
- Referrer gets a private message: `referral_reward_msg` (e.g. “Um novo membro entrou pelo seu link. Você ganhou 3 créditos”).

**When user taps “Ganhar Mídias Grátis”:**
- Bot sends `referral_copy`: text with `{link}`, `{count}` (convidados), `{credits}` (créditos para desbloqueio), in user’s language.

**Credits usage:** When a free user selects a creator (**sel:**), if they have credits and no active license, one credit is consumed and they get full access for that action (download all / view page) instead of previews.

So: **invite** = share ref link → new user signs up via link → referrer gets +3 credits and a message; **credits** = used to “unlock” one full access (search result) without paying.

---

## 6. Preview vs paywall (lock/unlock)

**Where:** `app/main.py` (on_callback_query, **sel:**), `app/users_db.py` (`check_preview_limit`, `increment_previews`, `is_license_active`)

**Logic when user selects a creator (sel:):**
1. Load user, get `has_access = is_license_active(user_id)` (VIP, credits, or God Mode).
2. If no access but `credits > 0`: use one credit, set `has_access = True`, show “using_credit” and full download buttons.
3. If `has_access`: show “model_found” + **BAIXAR TUDO** + **Ver Primeira Página** (no previews).
4. If not has_access:
   - If `not check_preview_limit(user_id)` → only `show_payment_popup` (no previews).
   - Else: `increment_previews(user_id)`, send 3 previews (fetch + upload), then `show_payment_popup`.

**Preview limit:** 3 per day (per user). `check_preview_limit` uses `daily_previews_used` and `last_preview_date`; resets when date changes.

So: **preview** = up to 3 items sent to the user per day when they don’t have access; **paywall** = after that, only payment options (and after payment, unlock = VIP = full download).

---

## 7. Language (PT / ES / EN)

**Where:** `app/languages.py`, `app/main.py`, `app/users_db.py`

- All user-facing strings go through `get_text(key, lang, **kwargs)` with `lang` from `u_data.get('language', 'pt')`.
- Language is set via **setlang:** callback and stored in DB (`user_db.update_user(user_id, language=...)`).
- Used in: welcome, buttons, search prompts, payment popups, referral, stats, errors, payment success/Pix messages.

---

## 8. Admin / God Mode

**Where:** `app/main.py` (keyboard, handle_message), `app/users_db.py` (`is_license_active`)

- **ADMIN_ID** from config; admin gets extra keyboard button **⚡ MODO GOD: {status}**.
- Tapping it toggles `is_god_mode` (0/1) in DB and refreshes the main keyboard.
- `is_license_active(admin)` returns True when God Mode is on (bypasses VIP and credits). So admin can test full flow without paying.

---

## 9. Downsell (payment popup with discount)

**Where:** `app/main.py` – `show_payment_popup(is_downsell=True)`

- **show_payment_popup** is called with `is_downsell=False` from VIP button and after previews.
- If you later trigger it with `is_downsell=True` (e.g. from a timer or another flow), it shows the same plan buttons but with `_ds` suffix: `buy:lifetime_ds`, `buy:monthly_ds`, `buy:weekly_ds`.
- In **buy:** handler, `_ds` is detected and price is multiplied by 0.7 (30% discount). So downsell = same UI, lower price at payment step.

---

## 10. Summary table

| Functionality   | Trigger / entry point                    | Main components                                      | Result |
|----------------|------------------------------------------|------------------------------------------------------|--------|
| Search         | “Buscar Modelo” or text while searching  | `smart_search`, `fetcher._get_creators_list`         | List of creators (buttons). |
| Fetch          | After selecting creator or download btn  | `fetcher.fetch_posts_paged`, `fetcher.download_media`| Files on disk (`downloads/`). |
| Upload         | After each fetch for user                | `uploader.upload_and_cleanup`                        | Photo/video in user chat; file deleted. |
| User interaction | Keyboard + inline callbacks             | `handle_message`, `on_callback_query`, `get_main_keyboard` | Menus, search, language, payment, download. |
| Invite         | Ref link `?start=ref{id}` + “Ganhar Mídias Grátis” | `process_referral`, referral_copy / referral_reward_msg | +3 credits to referrer, link + stats to user. |
| Preview        | Free user, creator selected, under limit | `check_preview_limit`, `increment_previews`, fetch 3, upload | 3 previews + payment popup. |
| Paywall / unlock | No access, no previews left or after payment | `show_payment_popup`, Stripe/Pix, `activate_license` | Payment or VIP/credits → full download. |
| Language       | “Idioma” or setlang callback             | `get_text`, `user_db.update_user(..., language=...)` | All copy in PT/ES/EN. |
| Admin / God Mode | “⚡ MODO GOD” (admin only)              | `is_god_mode` in DB, `is_license_active`            | Bypass paywall for testing. |

---

## 11. Bug fixes applied

1. **show_payment_popup:** The `if is_downsell:` block was empty and the keyboard was only built in `else`, so downsell never showed its own buttons. It’s now fixed: the keyboard is always built, and when `is_downsell` is True the callback_data uses `_ds` (e.g. `buy:weekly_ds`) so the existing **buy:** handler applies the 30% discount.

2. **dlpage callback_data parsing:** For `dlpage:service:c_id:offset:name` the code was reading `name = parts[3]` and `offset = int(parts[4])`, so name became the offset and offset could crash. Parsing is now: for **dlpage** use `offset = int(parts[3])`, `name = parts[4]`; for **dlall** use `name = ":".join(parts[3:])` so names containing colons are preserved.

3. **sel: and dlall/dlpage names with colons:** Callback_data uses `:` as separator; creator names can contain colons. Parsing now uses `split(":", 3)` or `split(":", 4)` and joins the last part(s) so `sel:service:id:Name: With: Colons` and similar are handled correctly.

---

**File reference:**  
- Fetch: `app/fetcher.py`  
- Upload: `app/uploader.py`  
- Search: `app/smart_search.py` + `app/main.py` (handle_message, sel:)  
- Invite: `app/main.py` (cmd_start ref, handle_message share) + `app/users_db.py` (process_referral)  
- User interaction / preview / paywall: `app/main.py` (handle_message, on_callback_query, show_payment_popup)
