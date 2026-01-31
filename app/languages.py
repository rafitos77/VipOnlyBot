
"""
Multi-language support module - v8.3 Global Edition
Provides high-conversion, niche-hot translations for PT, ES, and EN
"""

from typing import Dict, Any

TRANSLATIONS = {
    "pt": {
        # Welcome & Selection
        "select_lang": "🌐 **Selecione seu idioma / Select your language / Seleccione su idioma**",
        "welcome_title": "🔥 **BEM-VINDO AO SEU ACESSO PROIBIDO, {name}!** 🔥",
        "welcome_copy": (
            "Você acaba de desbloquear o portal para o **Acervo Privado** das maiores estrelas do OnlyFans, Patreon e Fansly. 🔞\n\n"
            "🚀 **O QUE VOCÊ PODE FAZER AGORA:**\n"
            "• Buscar qualquer modelo e ver o que ela esconde\n"
            "• Receber prévias exclusivas e picantes\n"
            "• Acessar o conteúdo **COMPLETO e SEM CENSURA** no VIP\n\n"
            "💎 **Chega de pagar caro. O conteúdo que você sempre quis está aqui.**"
        ),
        
        # Menu Buttons
        "btn_search": "🔍 Buscar Modelo",
        "btn_vip": "💎 Acesso VIP Total",
        "btn_help": "❓ Ajuda",
        "btn_lang": "🌐 Idioma",
        "btn_stats": "📊 Minha Conta",
        "btn_share": "🎁 Ganhar Mídias Grátis",
        "btn_god_mode": "⚡ MODO GOD: {status}",
        
        # Referral System
        "referral_title": "🎁 **GANHE ACESSO COMPLETO GRÁTIS!**",
        "referral_copy": (
            "Convide outros amantes de conteúdo exclusivo e seja recompensado:\n\n"
            "✅ Cada novo membro que entrar pelo seu link libera **3 mídias completas** para você!\n\n"
            "🔗 **Seu Link Secreto:**\n`{link}`\n\n"
            "👥 **Estatísticas:**\n"
            "• Amigos que entraram: {count}\n"
            "• Créditos para desbloqueio: {credits}\n\n"
            "📢 **DICA:** Compartilhe em grupos de nicho para encher seu saldo!"
        ),
        "referral_reward_msg": "🎉 **Parabéns!** Um novo membro entrou pelo seu link. Você ganhou **3 créditos** para desbloquear conteúdo completo!",
        
        # Search Flow
        "search_prompt": "✍️ **Digite o nome da modelo (OnlyFans, Patreon, etc.) que você deseja:**",
        "searching": "🔍 Vasculhando o acervo privado de **{name}**...",
        "no_media_found": "❌ **{name}** ainda não está em nosso acervo secreto. Tente outro nome!",
        "select_model": "✅ Encontramos essas deusas. Qual acervo você quer explorar?",
        
        # Download & Pages
        "model_found": "✅ **{name}** encontrada!\n\nVocê tem acesso total para baixar ou navegar.",
        "btn_download_all": "🚀 BAIXAR TUDO (Lote 50)",
        "btn_view_page": "📄 Ver Primeira Página",
        "sending_previews": "📤 Enviando 3 prévias de **{name}**...",
        "downloading": "⏳ Baixando **{name}**...",
        "download_complete": "✅ Download concluído!",
        "nothing_found": "❌ Nada encontrado.",
        
        # Payment/VIP Flow
        "vip_offer_title": "🔞 **ACESSO ILIMITADO DESBLOQUEADO!**",
        "vip_offer_copy": (
            "Pare de ver apenas prévias. Tenha o conteúdo **COMPLETO** e **SEM CENSURA** de todas as modelos, agora mesmo!\n\n"
            "✨ **Vantagens VIP:**\n"
            "• Download ilimitado de fotos e vídeos (OnlyFans, Patreon, Fansly)\n"
            "• Qualidade Máxima (4K Ultra HD)\n"
            "• Atualizações automáticas diárias do acervo\n\n"
            "👇 **Escolha seu plano e domine o acesso:**"
        ),
        "downsell_title": "🎁 **ESPERA! OFERTA RELÂMPAGO...**",
        "downsell_copy": "Vi que você hesitou. Liberei um **Plano Especial** com 30% de desconto para você garantir seu acesso total agora! Não perca essa chance de ouro. 😱",
        "payment_created_stripe": "✅ Pagamento criado! Finalize via Stripe.",
        "payment_created_pix": "✅ PIX gerado! Copie o código abaixo ou escaneie o QR Code.",
        "payment_created_pix_link": "🇧🇷 **PIX via Asaas**\n\n1) Clique no botão abaixo para abrir o link e pagar.\n2) Depois toque em **Confirmar pagamento** e envie o **ID da cobrança** (ex: `pay_xxxxx`).\n\nVocê também pode colar o link do comprovante.",
        "btn_open_payment_link": "🔗 Abrir link de pagamento",
        "btn_confirm_payment": "✅ Confirmar pagamento",
        "payment_prompt_asaas_id": "✅ Agora envie aqui o **ID da cobrança do Asaas** (ex: `pay_xxxxx`).\n\nPara cancelar: /cancel",
        "payment_invalid_asaas_id": "❌ ID inválido. Envie algo como `pay_xxxxx` (ou cole o link do comprovante).",
        "payment_cancelled": "✅ Ok, cancelado.",
        "payment_already_used": "⚠️ Esse ID de pagamento já foi usado por outro usuário.",
        "payment_not_pix": "⚠️ Esse pagamento não parece ser PIX.",
        "payment_amount_mismatch": "⚠️ O valor desse pagamento não corresponde ao plano escolhido. Gere um novo pagamento e tente novamente.",
        "payment_created_crypto": "✅ Pagamento cripto criado! Use o link/endereço abaixo para pagar.",
        "payment_check_failed": "❌ Não consegui verificar seu pagamento agora. Tente novamente em alguns minutos.",
        "btn_pay_stripe": "💳 Pagar (Stripe)",
        "btn_pay_pix": "🇧🇷 Pagar via PIX",
        "btn_pay_crypto": "🪙 Pagar com Cripto",
        "payment_choose_method": "💳 **Escolha a forma de pagamento**\n\nSelecione uma opção abaixo:",
        "payment_no_methods": (
            "⚠️ Nenhuma forma de pagamento está disponível no momento.\n\n"
            "Fale com o suporte/admin para ativar os gateways."
        ),
        "stripe_unavailable": (
            "⚠️ **Cartão/Stripe indisponível no momento** (método não habilitado).\n\n"
            "Escolha outra forma de pagamento:"
        ),
        "pix_unavailable": (
            "⚠️ **PIX indisponível no momento** (gateway não configurado).\n\n"
            "Escolha outra forma de pagamento:"
        ),
        "btn_check_payment": "✅ Já paguei (verificar)",
        "payment_confirmed": "✅ Pagamento confirmado! VIP ativado.",
        "payment_pending": "⏳ Ainda não consta como pago. Tente de novo em 1 minuto.",
        "payment_error": "❌ Erro ao gerar pagamento.",
        
        # God Mode
        "god_mode_on": "Ativado 🟢",
        "god_mode_off": "Desativado 🔴",
        "god_mode_msg": "⚡ **MODO GOD ALTERNADO:** Agora você está operando como **{mode}**.",
        
        # Other
        "error_occurred": "❌ Ops! Algo deu errado. Tente novamente ou contate o suporte: {error}",
        "search_usage": "❌ Digite o nome da modelo ou use o botão de busca.",
        "loading": "🔄 Carregando...",
        "using_credit": "🎫 **Usando 1 crédito de desbloqueio para liberar este conteúdo...**",
    },
    
    "es": {
        # Welcome & Selection
        "select_lang": "🌐 **Seleccione su idioma**",
        "welcome_title": "🔥 **¡BIENVENIDO A TU ACCESO PROHIBIDO, {name}!** 🔥",
        "welcome_copy": (
            "Acabas de desbloquear el portal al **Archivo Privado** de las estrellas más grandes de OnlyFans, Patreon y Fansly. 🔞\n\n"
            "🚀 **QUÉ PUEDES HACER AHORA:**\n"
            "• Buscar cualquier modelo y ver lo que esconde\n"
            "• Recibir vistas previas exclusivas y picantes\n"
            "• Acceder al contenido **COMPLETO y SIN CENSURA** en el VIP\n\n"
            "💎 **Deja de pagar caro. El contenido que siempre quisiste está aquí.**"
        ),
        
        # Menu Buttons
        "btn_search": "🔍 Buscar Modelo",
        "btn_vip": "💎 Acceso VIP Total",
        "btn_help": "❓ Ayuda",
        "btn_lang": "🌐 Idioma",
        "btn_stats": "📊 Mi Cuenta",
        "btn_share": "🎁 Ganar Medios Gratis",
        "btn_god_mode": "⚡ MODO GOD: {status}",
        
        # Referral System
        "referral_title": "🎁 **¡GANA ACCESO COMPLETO GRATIS!**",
        "referral_copy": (
            "Invita a otros amantes de contenido exclusivo y sé recompensado:\n\n"
            "✅ ¡Cada nuevo miembro que entre por tu enlace libera **3 medios completos** para ti!\n\n"
            "🔗 **Tu Enlace Secreto:**\n`{link}`\n\n"
            "👥 **Estadísticas:**\n"
            "• Amigos que se unieron: {count}\n"
            "• Créditos para desbloqueo: {credits}\n\n"
            "📢 **CONSEJO:** ¡Comparte en grupos de nicho para llenar tu saldo!"
        ),
        "referral_reward_msg": "🎉 **¡Felicidades!** Un nuevo miembro entró por tu enlace. ¡Has ganado **3 créditos** para desbloquear contenido completo!",
        
        # Search Flow
        "search_prompt": "✍️ **Escribe el nombre de la modelo (OnlyFans, Patreon, etc.) que deseas:**",
        "searching": "🔍 Buscando en el archivo privado de **{name}**...",
        "no_media_found": "❌ **{name}** aún no está en nuestro archivo secreto. ¡Intenta con otro nombre!",
        "select_model": "✅ Encontramos estas diosas. ¿Qué archivo quieres explorar?",
        
        # Download & Pages
        "model_found": "✅ ¡**{name}** encontrada!\n\nTienes acceso total para descargar o navegar.",
        "btn_download_all": "🚀 DESCARGAR TODO (Lote 50)",
        "btn_view_page": "📄 Ver Primera Página",
        "sending_previews": "📤 Enviando 3 vistas previas de **{name}**...",
        "downloading": "⏳ Descargando **{name}**...",
        "download_complete": "✅ ¡Descarga completada!",
        "nothing_found": "❌ No se encontró nada.",
        
        # Payment/VIP Flow
        "vip_offer_title": "🔞 **¡ACCESO ILIMITADO DESBLOQUEADO!**",
        "vip_offer_copy": (
            "Deja de ver solo vistas previas. ¡Ten el contenido **COMPLETO** y **SIN CENSURA** de todas las modelos, ahora mismo!\n\n"
            "✨ **Ventajas VIP:**\n"
            "• Descarga ilimitada de fotos y videos (OnlyFans, Patreon, Fansly)\n"
            "• Calidad Máxima (4K Ultra HD)\n"
            "• Actualizaciones automáticas diarias del archivo\n\n"
            "👇 **Elige tu plan y domina el acceso:**"
        ),
        "downsell_title": "🎁 **¡ESPERA! OFERTA RELÂMPAGO...**",
        "downsell_copy": "Vi que dudaste. ¡He liberado un **Plan Especial** con 30% de descuento para que asegures tu acceso total ahora! No pierdas esta oportunidad de oro. 😱",
        "payment_created_stripe": "✅ Pago creado. Finaliza vía Stripe.",
        "payment_created_pix": "✅ PIX generado. Copia el código o escanea el QR.",
        "payment_created_pix_link": "🇧🇷 **PIX vía Asaas**\n\n1) Abre el enlace de pago y paga.\n2) Luego toca **Confirmar pago** y envía el **ID del pago** (ej: `pay_xxxxx`).",
        "btn_open_payment_link": "🔗 Abrir enlace de pago",
        "btn_confirm_payment": "✅ Confirmar pago",
        "payment_prompt_asaas_id": "✅ Ahora envía aquí el **ID del pago de Asaas** (ej: `pay_xxxxx`).\n\nPara cancelar: /cancel",
        "payment_invalid_asaas_id": "❌ ID inválido. Envía algo como `pay_xxxxx` (o pega el enlace del comprobante).",
        "payment_cancelled": "✅ Ok, cancelado.",
        "payment_already_used": "⚠️ Este ID de pago ya fue usado por otro usuario.",
        "payment_not_pix": "⚠️ Este pago no parece ser PIX.",
        "payment_amount_mismatch": "⚠️ El monto no coincide con el plan. Genera un nuevo pago e intenta de nuevo.",
        "payment_created_crypto": "✅ Pago cripto creado. Usa el enlace/dirección abajo para pagar.",
        "btn_pay_stripe": "💳 Pagar (Stripe)",
        "btn_pay_pix": "🇧🇷 Pagar con PIX",
        "btn_pay_crypto": "🪙 Pagar con Cripto",
        "payment_choose_method": "💳 **Elige el método de pago**\n\nSelecciona una opción:",
        "payment_no_methods": (
            "⚠️ No hay métodos de pago disponibles en este momento.\n\n"
            "Contacta al soporte/admin para activar los gateways."
        ),
        "stripe_unavailable": (
            "⚠️ **Stripe/tarjeta no disponible por ahora** (método no habilitado).\n\n"
            "Elige otra forma de pago:"
        ),
        "pix_unavailable": (
            "⚠️ **PIX no disponible por ahora** (gateway no configurado).\n\n"
            "Elige otra forma de pago:"
        ),
        "btn_check_payment": "✅ Ya pagué (verificar)",
        "payment_confirmed": "✅ Pago confirmado. ¡VIP activado!",
        "payment_pending": "⏳ Aún no figura como pagado. Intenta de nuevo en 1 minuto.",
        "payment_error": "❌ Error al generar el pago.",
        
        # God Mode
        "god_mode_on": "Activado 🟢",
        "god_mode_off": "Desactivado 🔴",
        "god_mode_msg": "⚡ **MODO GOD ALTERNADO:** Ahora estás operando como **{mode}**.",
        
        # Other
        "error_occurred": "❌ ¡Ops! Algo salió mal. Intenta de nuevo o contacta a soporte: {error}",
        "search_usage": "❌ Escribe el nombre de la modelo o usa el botón de búsqueda.",
        "loading": "🔄 Cargando...",
        "using_credit": "🎫 **Usando 1 crédito de desbloqueo para liberar este contenido...**",
    },
    
    "en": {
        # Welcome & Selection
        "select_lang": "🌐 **Select your language**",
        "welcome_title": "🔥 **WELCOME TO YOUR FORBIDDEN ACCESS, {name}!** 🔥",
        "welcome_copy": (
            "You have just unlocked the portal to the **Private Vault** of the biggest stars on OnlyFans, Patreon, and Fansly. 🔞\n\n"
            "🚀 **WHAT YOU CAN DO NOW:**\n"
            "• Search for any model and see what she's hiding\n"
            "• Receive exclusive and spicy previews\n"
            "• Access the **FULL and UNCENSORED** content in VIP\n\n"
            "💎 **Stop overpaying. The content you always wanted is here.**"
        ),
        
        # Menu Buttons
        "btn_search": "🔍 Search Model",
        "btn_vip": "💎 Total VIP Access",
        "btn_help": "❓ Help",
        "btn_lang": "🌐 Language",
        "btn_stats": "📊 My Account",
        "btn_share": "🎁 Get Free Media",
        "btn_god_mode": "⚡ GOD MODE: {status}",
        
        # Referral System
        "referral_title": "🎁 **GET FREE FULL ACCESS!**",
        "referral_copy": (
            "Invite other exclusive content lovers and get rewarded:\n\n"
            "✅ Every new member who joins via your link unlocks **3 full media** for you!\n\n"
            "🔗 **Your Secret Link:**\n`{link}`\n\n"
            "👥 **Stats:**\n"
            "• Friends who joined: {count}\n"
            "• Unlock credits: {credits}\n\n"
            "📢 **TIP:** Share in niche groups to fill your balance!"
        ),
        "referral_reward_msg": "🎉 **Congratulations!** A new member joined through your link. You earned **3 credits** to unlock full content!",
        
        # Search Flow
        "search_prompt": "✍️ **Type the name of the model (OnlyFans, Patreon, etc.) you want:**",
        "searching": "🔍 Searching through the private vault of **{name}**...",
        "no_media_found": "❌ **{name}** is not in our secret vault yet. Try another name!",
        "select_model": "✅ We found these goddesses. Which vault do you want to explore?",
        
        # Download & Pages
        "model_found": "✅ **{name}** found!\n\nYou have full access to download or browse.",
        "btn_download_all": "🚀 DOWNLOAD ALL (Batch 50)",
        "btn_view_page": "📄 View First Page",
        "sending_previews": "📤 Sending 3 previews of **{name}**...",
        "downloading": "⏳ Downloading **{name}**...",
        "download_complete": "✅ Download complete!",
        "nothing_found": "❌ Nothing found.",
        
        # Payment/VIP Flow
        "vip_offer_title": "🔞 **UNLIMITED ACCESS UNLOCKED!**",
        "vip_offer_copy": (
            "Stop watching just previews. Get the **FULL** and **UNCENSORED** content from all models, right now!\n\n"
            "✨ **VIP Advantages:**\n"
            "• Unlimited photo and video downloads (OnlyFans, Patreon, Fansly)\n"
            "• Maximum Quality (4K Ultra HD)\n"
            "• Daily automatic vault updates\n\n"
            "👇 **Choose your plan and dominate access:**"
        ),
        "downsell_title": "🎁 **WAIT! FLASH OFFER...**",
        "downsell_copy": "I saw you hesitated. I've unlocked a **Special Plan** with 30% discount for you to secure your total access now! Don't miss this golden opportunity. 😱",
        "payment_created_stripe": "✅ Payment created. Complete it via Stripe.",
        "payment_created_pix": "✅ PIX created. Copy the code or scan the QR.",
        "payment_created_pix_link": "🇧🇷 **PIX via Asaas**\n\n1) Open the payment link below and pay.\n2) Then tap **Confirm payment** and send the **Asaas payment ID** (e.g. `pay_xxxxx`).",
        "btn_open_payment_link": "🔗 Open payment link",
        "btn_confirm_payment": "✅ Confirm payment",
        "payment_prompt_asaas_id": "✅ Now send the **Asaas payment ID** here (e.g. `pay_xxxxx`).\n\nTo cancel: /cancel",
        "payment_invalid_asaas_id": "❌ Invalid ID. Send something like `pay_xxxxx` (or paste the receipt link).",
        "payment_cancelled": "✅ OK, cancelled.",
        "payment_already_used": "⚠️ This payment ID was already used by another user.",
        "payment_not_pix": "⚠️ This payment does not look like PIX.",
        "payment_amount_mismatch": "⚠️ The amount does not match the selected plan. Generate a new payment and try again.",
        "payment_created_crypto": "✅ Crypto payment created. Use the link/address below to pay.",
        "btn_pay_stripe": "💳 Pay (Stripe)",
        "btn_pay_pix": "🇧🇷 Pay with PIX",
        "btn_pay_crypto": "🪙 Pay with Crypto",
        "payment_choose_method": "💳 **Choose your payment method**\n\nSelect an option below:",
        "payment_no_methods": (
            "⚠️ No payment methods are available right now.\n\n"
            "Ask support/admin to enable the gateways."
        ),
        "stripe_unavailable": (
            "⚠️ **Card/Stripe is temporarily unavailable** (method not enabled).\n\n"
            "Choose another payment method:"
        ),
        "pix_unavailable": (
            "⚠️ **PIX is temporarily unavailable** (gateway not configured).\n\n"
            "Choose another payment method:"
        ),
        "btn_check_payment": "✅ I paid (check)",
        "payment_confirmed": "✅ Payment confirmed! VIP activated.",
        "payment_pending": "⏳ Not marked as paid yet. Try again in 1 minute.",
        "payment_error": "❌ Error generating payment.",
        
        # God Mode
        "god_mode_on": "Enabled 🟢",
        "god_mode_off": "Disabled 🔴",
        "god_mode_msg": "⚡ **GOD MODE TOGGLED:** You are now operating as **{mode}**.",
        
        # Other
        "error_occurred": "❌ Oops! Something went wrong. Try again or contact support: {error}",
        "search_usage": "❌ Type the model name or use the search button.",
        "loading": "🔄 Loading...",
        "using_credit": "🎫 **Using 1 unlock credit to release this content...**",
    }
}


def get_text(key: str, lang: str = "pt", **kwargs) -> str:
    """
    Get translated text for a given key and language
    """
    if lang not in TRANSLATIONS:
        lang = "pt"
    
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS["pt"].get(key, key))
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            pass
    
    return text


def get_all_langs() -> list:
    """Get list of all supported languages"""
    return list(TRANSLATIONS.keys())
