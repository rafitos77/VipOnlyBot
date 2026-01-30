# 💎 Bot VIP Telegram - Versão Sênior (v5.1)

Esta versão foi reconstruída com uma arquitetura de **Lazy Loading** e **Isolamento de Módulos** para garantir que o bot nunca mais sofra crashes de importação no Railway.

## 🛠️ Por que esta versão é superior?
1.  **Arquitetura Anti-Crash**: Os módulos são carregados apenas quando necessários, eliminando dependências circulares que causavam o erro `ModuleNotFoundError`.
2.  **Inicialização Robusta**: O `main.py` agora gerencia o ciclo de vida do bot de forma assíncrona e segura, com logs detalhados para facilitar o diagnóstico.
3.  **Compatibilidade Total com Railway**: Estrutura otimizada para detecção automática e persistência de dados via volumes.

## 🚀 Como fazer o Deploy Definitivo
1.  **GitHub**: Suba todos os arquivos da pasta `bot_senior` para a raiz do seu repositório.
2.  **Railway**:
    *   Conecte o repositório.
    *   O Railway detectará o `main.py` e o `requirements.txt` automaticamente.
3.  **Variáveis de Ambiente**: Certifique-se de configurar:
    *   `BOT_TOKEN`
    *   `ADMIN_ID`
    *   `PAYPAL_CLIENT_ID`
    *   `PAYPAL_CLIENT_SECRET`
    *   `PAYPAL_MODE` (live)

## 🛡️ Persistência
Para não perder as licenças, adicione um **Volume** no Railway montado em `/data`. O bot salvará o banco de dados lá automaticamente.

---
**Status do Sistema:** ✅ Testado e Validado (Smoke Test & Integration Test Passed).
