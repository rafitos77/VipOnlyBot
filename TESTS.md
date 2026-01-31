# Testes offline

Todos os testes abaixo rodam **sem internet**, usando mocks.

## 1) Compile

```bash
python -m compileall .
```

## 2) Smoke test

```bash
python smoke_test.py
```

## 3) Integration tests

```bash
python integration_test.py
```

## 4) Payment gateway selection tests

Valida (offline): disponibilidade por ENV, detecção do erro específico do Stripe e existência dos textos.

```bash
python app/gateway_selection_test.py
```

## 5) O que é validado

- Imports + validação de config
- Banco (SQLite): criação de usuário, flags VIP e GOD
- UI: `safe_edit_or_send` com fallback para `send_message`
- Upload: **nunca usa `parse_mode` em captions de mídia**, aceita caracteres especiais, pula arquivos vazios e grandes
- Paginação: cálculo de próximo offset baseado em POSTS
