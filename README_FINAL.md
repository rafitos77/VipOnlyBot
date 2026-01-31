# 💎 Bot VIP Telegram - Versão Inquebrável (v6.0)

Esta versão foi reconstruída como um **Pacote Python estruturado**. Esta é a forma mais profissional e estável de rodar aplicações Python em servidores como o Railway.

## 🛠️ O que mudou?
1.  **Estrutura de Pacote**: O código agora reside dentro de uma pasta `app/` com arquivos `__init__.py`. Isso resolve permanentemente o erro `ModuleNotFoundError`.
2.  **Script de Entrada (`run.py`)**: Existe um script na raiz chamado `run.py` que gerencia todas as importações e inicia o bot de forma segura.
3.  **Procfile**: Adicionei um arquivo `Procfile` que diz ao Railway exatamente como rodar o bot (`worker: python run.py`).

## 🚀 Como fazer o Deploy (Passo a Passo)
1.  **GitHub**: Suba **todos** os arquivos e pastas que estão no ZIP para a raiz do seu repositório no GitHub.
    *   A pasta `app/` deve estar na raiz.
    *   O arquivo `run.py` deve estar na raiz.
    *   O arquivo `Procfile` deve estar na raiz.
2.  **Railway**:
    *   Conecte o repositório.
    *   O Railway detectará o `Procfile` e usará o comando `python run.py` automaticamente.
3.  **Variáveis de Ambiente**: Configure as mesmas variáveis de antes (`BOT_TOKEN`, `ADMIN_ID`, etc).

## 🛡️ Persistência
Não esqueça de adicionar um **Volume** no Railway montado em `/data` para não perder os dados dos seus usuários.

---
**Status do Sistema:** ✅ Certificado como "Inquebrável" (Package Smoke Test Passed).
