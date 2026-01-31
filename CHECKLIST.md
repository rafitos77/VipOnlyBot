# Checklist de produção

## Telegram / UI
- [x] **Nunca** usa `parse_mode` em caption de mídia (foto/vídeo/document/media_group).
- [x] Markdown somente em mensagens de texto (`send_message` / `edit_message_text`) com escape nos trechos dinâmicos.
- [x] `safe_edit_or_send` em callbacks com fallback para `send_message`.
- [x] `application.add_error_handler(...)` global.

## Instância única (evitar 409 Conflict)
- [x] Documento orienta `replicas=1` no Railway.
- [x] Lock por arquivo (`/data/bot.lock` ou `BOT_LOCK_PATH`).
- [x] Processo encerra se lock já existir.

## Paginação / Slots
- [x] Sessão por usuário+creator em memória.
- [x] `next_offset` calculado por **número de POSTS** retornados pela API.
- [x] Após cada página: botões **▶️ Próxima página** e **⛔ Parar**.
- [x] Só exibe "✅ Download completo" quando não há mais posts.

## Uploader / Guardrails
- [x] Pula arquivos 0 bytes.
- [x] Pula arquivos acima de `TELEGRAM_MAX_UPLOAD_MB`.
- [x] Não faz retry em erros não-retryáveis (413, empty, entity parse etc.).
- [x] Logs com contadores por página.

## Admin GOD Mode
- [x] Toggle grava no DB (`is_god_mode`).
- [x] `ADMIN_FORCE_VIP=1` força VIP (se setado).
- [x] Caso contrário: VIP efetivo = `is_god_mode` OR `is_vip`.
- [x] `ADMIN_GOD_MODE=1` só define estado inicial, não bloqueia desligar.

## Testes
- [x] `python -m compileall .`
- [x] `python smoke_test.py`
- [x] `python integration_test.py`
