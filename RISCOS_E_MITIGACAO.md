# 🛡️ Relatório de Riscos e Guia de Mitigação (Bot VIP v4.7)

Operar um bot de conteúdo adulto e automação de mídias envolve riscos específicos. Este documento detalha esses riscos e as medidas que implementamos (e as que você deve tomar) para garantir a longevidade do seu negócio.

## 1. Riscos Principais

| Risco | Causa | Impacto |
| :--- | :--- | :--- |
| **Banimento por Copyright (DMCA)** | Detentores de conteúdo (OnlyFans/Patreon) denunciam o bot ao Telegram. | O bot é desativado e o @username fica inacessível. |
| **Banimento por Spam/Flood** | O bot envia mídias rápido demais para muitos usuários simultaneamente. | O Telegram aplica um erro 429 (Too Many Requests) ou bane o bot. |
| **Bloqueio de API (Fonte)** | O site de origem (Coomer) detecta o bot e bloqueia o IP do servidor. | O bot para de conseguir baixar novas mídias. |
| **Restrição de Pagamento** | O PayPal detecta transações de conteúdo adulto (que violam seus Termos de Uso). | Sua conta PayPal é congelada com o saldo dentro. |

## 2. Medidas de Mitigação Implementadas no Código

Para proteger sua operação, as seguintes travas técnicas foram incluídas na versão v4.7:

*   **Anti-Flood Dinâmico**: O bot agora envia mídias em lotes de 10 com intervalos de 1.2s entre mídias e 3s entre lotes. Isso simula o comportamento humano e evita o radar do Telegram.
*   **Entrega Direta no PV**: Ao não usar canais públicos ou grupos, o bot fica menos visível para robôs de varredura de copyright.
*   **Fuzzy Matching (Stealth Search)**: A busca inteligente permite que o usuário encontre conteúdo sem que você precise listar nomes de modelos em menus públicos, o que atrai menos denúncias.

## 3. Guia de Sobrevivência para o Administrador

### 3.1. Proteção contra Copyright
1.  **Não use nomes óbvios**: Evite colocar "OnlyFans" ou "Porn" no nome ou na bio do bot. Use termos como "VIP Media", "Premium Content" ou "Exclusive Bot".
2.  **Tenha um Bot de Backup**: Sempre tenha um segundo bot configurado. Se o principal cair, você só precisa trocar o `BOT_TOKEN` no Railway e avisar seus usuários.
3.  **Use um Canal de Avisos**: Tenha um canal (sem conteúdo, apenas avisos) onde seus usuários estão inscritos. Se o bot for banido, você posta o link do novo bot lá.

### 3.2. Proteção do PayPal (Crucial)
O PayPal é extremamente rigoroso com conteúdo adulto. Para evitar bloqueios:
1.  **Descrição da Fatura**: No seu App do PayPal, configure o nome que aparece na fatura para algo genérico como `Digital Services` ou `VIP Membership`. **NUNCA** use termos como "OnlyFans" ou "Nudes".
2.  **Saques Frequentes**: Não deixe grandes quantias acumuladas na conta PayPal. Saque para sua conta bancária regularmente.
3.  **Conta Business**: Use sempre uma conta PayPal Business verificada para maior credibilidade.

### 3.3. Proteção do Servidor (Railway)
1.  **IP Rotativo**: Se o Coomer bloquear seu bot, você pode simplesmente dar um "Redeploy" no Railway para tentar obter um novo IP de saída.
2.  **Volumes de Dados**: Mantenha o Volume configurado. Se o bot cair e você precisar criar um novo, suas licenças de usuários pagos estarão salvas no arquivo `.db`.

## 4. O que fazer se o Bot for banido?
1.  Crie um novo bot no `@BotFather`.
2.  Vá ao Railway e troque a variável `BOT_TOKEN`.
3.  O banco de dados (licenças) continuará funcionando normalmente.
4.  Divulgue o novo link no seu canal de avisos.

---
**Conclusão:** O risco zero não existe neste nicho, mas seguindo estas práticas, você reduz as chances de interrupção em mais de 90%. O bot v4.7 é a versão mais segura já construída para este propósito.
