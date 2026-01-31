"""app.final_validation_zero_erro

Validação local (offline) para garantir:
- Imports e configuração base
- Regras de preview/reset
- Pricing e downsell
- Roteamento de pagamentos (Stripe vs PushinPay) sem chamar APIs externas
- Integridade de arquivos essenciais para deploy no Railway

Rode assim:
  python app/final_validation_zero_erro.py
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Mock minimal env
os.environ.setdefault("BOT_TOKEN", "123456789:ABCDEF-GHIJKL-MNOPQRSTUV")
os.environ.setdefault("ADMIN_ID", "12345")


async def run_final_validation() -> None:
    print("🚀 INICIANDO VALIDAÇÃO FINAL EXAUSTIVA (v8.3 - Offline)\n")

    from app.users_db import UserDB
    from app.smart_search import smart_search
    from app.payments import payment_provider_for

    db_path = "zero_erro_test.db"
    user_db = UserDB(db_path)

    # --- 1. Admin bypass ---
    print("--- 1. Teste de Admin Bypass ---")
    admin_id = int(os.environ.get("ADMIN_ID", "12345"))
    # Admin bypass depends on GOD MODE flag in this codebase
    user_db.update_user(
        admin_id,
        is_god_mode=1,
        daily_previews_used=99,
        last_preview_date=datetime.now().date().isoformat(),
    )
    assert user_db.is_license_active(admin_id) is True
    print(f"✅ Admin (ID {admin_id}) ignorando limites: OK")

    # --- 2. Smart search ---
    print("\n--- 2. Teste de Busca Inteligente ---")
    mock_creators = [
        {"name": "Belle Delphine", "service": "coomer", "id": "belle"},
        {"name": "Amouranth", "service": "coomer", "id": "amo"},
    ]
    matches = smart_search.find_similar("beledelphine", mock_creators)
    assert matches and matches[0]["id"] == "belle"
    print("✅ Fuzzy match: OK")

    # --- 3. Preview limit + daily reset ---
    print("\n--- 3. Teste de Limite de Preview e Reset Diário ---")
    user_id = 67890
    # Simula que ontem já tinha usado previews, hoje deve resetar
    user_db.update_user(
        user_id,
        daily_previews_used=3,
        last_preview_date=(datetime.now() - timedelta(days=1)).date().isoformat(),
    )
    assert user_db.check_preview_limit(user_id) is True
    # Consome 3 e bloqueia o 4
    user_db.update_user(user_id, daily_previews_used=0, last_preview_date=datetime.now().date().isoformat())
    assert user_db.check_preview_limit(user_id) is True
    user_db.increment_previews(user_id)
    user_db.increment_previews(user_id)
    user_db.increment_previews(user_id)
    assert user_db.check_preview_limit(user_id) is False
    print("✅ Preview limit + reset: OK")

    # --- 4. Pricing + downsell ---
    print("\n--- 4. Teste de Pricing e Downsell ---")
    pricing_pt = user_db.get_pricing("pt")
    weekly = float(pricing_pt["weekly"]["price"])
    downsell = weekly * 0.7
    assert downsell > 0
    print(f"✅ Downsell calculado: {weekly:.2f} -> {downsell:.2f}")

    # --- 5. Payment routing ---
    print("\n--- 5. Teste de Roteamento de Pagamento ---")
    assert payment_provider_for("pt", "BRL") == "pushinpay"
    assert payment_provider_for("en", "USD") == "stripe"
    print("✅ Routing Stripe/PushinPay: OK")

    # --- 6. Files required for Railway ---
    print("\n--- 6. Verificação de Integridade de Arquivos (Deploy Railway) ---")
    required = [
        os.path.join(PROJECT_ROOT, "run.py"),
        os.path.join(PROJECT_ROOT, "Procfile"),
        os.path.join(PROJECT_ROOT, "requirements.txt"),
        os.path.join(PROJECT_ROOT, "app", "main.py"),
        os.path.join(PROJECT_ROOT, "app", "users_db.py"),
        os.path.join(PROJECT_ROOT, "app", "payments.py"),
    ]
    missing = [p for p in required if not os.path.exists(p)]
    assert not missing, f"Missing files: {missing}"
    print("✅ Arquivos essenciais presentes: OK")

    print("\n✅ VALIDAÇÃO CONCLUÍDA: offline checks passaram.")

    try:
        os.remove(db_path)
    except OSError:
        pass


if __name__ == "__main__":
    asyncio.run(run_final_validation())
