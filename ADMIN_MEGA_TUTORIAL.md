# 🚀 MEGA TUTORIAL DO ADMINISTRADOR: Bot VIP v4.5 (Edição Escalável)

Este bot foi transformado em uma máquina de vendas automática. Ele não apenas entrega conteúdo, mas utiliza gatilhos mentais de dopamina, urgência e um sistema de remarketing agressivo para garantir que você maximize seus lucros.

## 1. Funções de Alta Conversão (O Segredo do Lucro)

| Funcionalidade | Gatilho Mental | Como Funciona |
| :--- | :--- | :--- |
| **Preview de 3 Mídias** | Reciprocidade/Dopamina | O usuário recebe 3 mídias reais no PV. Isso gera dopamina e desejo por mais. |
| **Popup de Urgência** | Escassez/Urgência | Após o limite, o bot avisa que restam apenas 5 vagas promocionais. |
| **Remarketing Automático** | Persistência | Se o usuário clicar em comprar mas não pagar, o bot manda uma mensagem após 15 min. |
| **Downsell (30% OFF)** | Oportunidade | No remarketing, o bot oferece o Plano Semanal com 30% de desconto para fechar a venda. |
| **Acesso Admin Total** | Autoridade | Você (Admin) tem acesso ilimitado a todas as buscas e mídias sem pagar nada. |

## 2. Configuração das Contas (Vincular PayPal)

### 2.1. PayPal (Onde você recebe o dinheiro)
1.  Acesse [PayPal Developer](https://developer.paypal.com/).
2.  Crie um App em **Apps & Credentials**.
3.  Copie o **Client ID** e o **Secret**.
4.  No Railway, defina `PAYPAL_MODE=live` para receber dinheiro real.

### 2.2. Seu ID de Administrador
1.  Descubra seu ID no bot `@userinfobot`.
2.  Coloque esse número na variável `ADMIN_ID` no Railway.
3.  **Vantagem:** Você poderá usar o bot para baixar qualquer conteúdo sem restrições.

## 3. Tabela de Preços Otimizada (Dopamina)

Os preços foram reduzidos para criar um efeito de "compra por impulso":

| Plano | Brasil (BRL) | LATAM (USD) | Global (USD) |
| :--- | :--- | :--- | :--- |
| **Semanal** | R$ 9,90 | $1.99 | $5.00 |
| **Mensal** | R$ 29,90 | $5.99 | $14.00 |
| **Vitalício** | **R$ 59,90** | **$12.99** | **$25.00** |

*Nota: O Plano Vitalício é destacado como o "Melhor Valor" para incentivar o ticket mais alto.*

## 4. Comandos de Administração

| Comando | Descrição |
| :--- | :--- |
| `/start` | Inicia o bot e verifica seu status (Admin ou Usuário). |
| `/search <nome>` | Busca modelos. Admin baixa tudo; Usuário baixa 3 e depois vê o checkout. |
| `/stats` | Veja quantos usuários e buscas seu bot está processando. |
| `/addadmin <id>` | Autorize um sócio ou moderador a usar o bot sem limites. |

## 5. Guia de Deploy (Railway)

1.  **GitHub:** Suba a pasta `bot/` para um repositório privado.
2.  **Railway:** Conecte o repositório.
3.  **Variáveis:** Adicione `BOT_TOKEN`, `ADMIN_ID`, `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_MODE`.
4.  **Volume:** Adicione um Volume montado em `/app/bot/` para salvar o banco de dados `bot_data.db`.
5.  **Comando:** O comando de início deve ser `python bot/main_pv.py`.

---
**⚠️ AVISO:** Este sistema foi testado e validado. A precisão das mídias é garantida pela busca inteligente. Se o usuário digitar "beledelphine", o bot encontrará "Belle Delphine" e entregará as mídias dela.
