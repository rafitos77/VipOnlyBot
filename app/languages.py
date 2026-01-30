
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
        "order_created": "✅ Ordem criada! Pague {label} via PayPal.",
        "btn_pay_paypal": "💳 Pagar com PayPal",
        "btn_pay_stripe": "💳 Pagar com Stripe",
        "stripe_invoice_title": "💎 Acesso VIP Total",
        "stripe_invoice_description": "Desbloqueio de acesso VIP ({label}) ao acervo privado.",
        "payment_success": "✅ Pagamento recebido com sucesso! Seu acesso VIP foi ativado. Bem-vindo!",
        "payment_success_no_plan": "✅ Pagamento recebido com sucesso! No entanto, não conseguimos identificar o plano. Por favor, entre em contato com o suporte.",
        "payment_error_payload": "❌ Erro no pagamento: Payload da fatura inválido.",
        "payment_error_unsupported_currency": "❌ Erro: Moeda não suportada para este método de pagamento.",
        "payment_error_pix_not_implemented": "❌ Erro: O Pix ainda não foi implementado. Por favor, utilize o Stripe.",
        "payment_error": "❌ Erro ao gerar pagamento.",
        "payment_error_pix": "❌ Erro ao gerar pagamento Pix. Tente novamente.",
        "pix_invoice_title": "💎 Acesso VIP Total - Pix",
        "pix_invoice_description": "Desbloqueio de acesso VIP ({label}) via Pix.",
        "pix_order_created": "✅ **Pedido Pix Criado!**\n\nValor: **{label}**\n\nEscaneie o QR Code abaixo ou copie o código Pix para pagar. Após o pagamento, clique no botão abaixo para confirmar.",
        "btn_pix_confirm": "✅ Já Paguei - Verificar Pagamento",
        "pix_scan_qr": "📱 **Escaneie o QR Code com seu app bancário ou copie o código Pix acima.**",
        "checking_payment": "🔍 Verificando pagamento...",
        "payment_still_pending": "⏳ Pagamento ainda pendente. Aguarde alguns segundos e tente novamente.",
        "payment_check_error": "❌ Erro ao verificar pagamento. Tente novamente em alguns instantes.",
        "payment_not_found": "❌ Transação não encontrada. Entre em contato com o suporte.",
        
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
        "order_created": "✅ ¡Orden creada! Paga {label} vía PayPal.",
        "btn_pay_paypal": "💳 Pagar con PayPal",
        "btn_pay_stripe": "💳 Pagar con Stripe",
        "stripe_invoice_title": "💎 Acceso VIP Total",
        "stripe_invoice_description": "Desbloqueo de acceso VIP ({label}) al archivo privado.",
        "payment_success": "✅ ¡Pago recibido con éxito! Tu acceso VIP ha sido activado. ¡Bienvenido!",
        "payment_success_no_plan": "✅ ¡Pago recibido con éxito! Sin embargo, no pudimos identificar el plan. Por favor, contacta con soporte.",
        "payment_error_payload": "❌ Error de pago: Carga útil de la factura inválida.",
        "payment_error_unsupported_currency": "❌ Error: Moneda no soportada para este método de pago.",
        "payment_error_pix_not_implemented": "❌ Error: Pix aún no ha sido implementado. Por favor, utiliza Stripe.",
        "payment_error": "❌ Error al generar el pago.",
        "payment_error_pix": "❌ Error al generar el pago Pix. Intenta de nuevo.",
        "pix_invoice_title": "💎 Acceso VIP Total - Pix",
        "pix_invoice_description": "Desbloqueo de acceso VIP ({label}) vía Pix.",
        "pix_order_created": "✅ **¡Pedido Pix Creado!**\n\nMonto: **{label}**\n\nEscanea el código QR a continuación o copia el código Pix para pagar. Después del pago, haz clic en el botón a continuación para confirmar.",
        "btn_pix_confirm": "✅ Ya Pagué - Verificar Pago",
        "pix_scan_qr": "📱 **Escanea el código QR con tu aplicación bancaria o copia el código Pix arriba.**",
        "checking_payment": "🔍 Verificando pago...",
        "payment_still_pending": "⏳ Pago aún pendiente. Espera unos segundos e intenta de nuevo.",
        "payment_check_error": "❌ Error al verificar el pago. Intenta de nuevo en un momento.",
        "payment_not_found": "❌ Transacción no encontrada. Por favor, contacta con soporte.",
        
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
        "order_created": "✅ Order created! Pay {label} via PayPal.",
        "btn_pay_paypal": "💳 Pay with PayPal",
        "btn_pay_stripe": "💳 Pay with Stripe",
        "stripe_invoice_title": "💎 Total VIP Access",
        "stripe_invoice_description": "VIP access unlock ({label}) to the private vault.",
        "payment_success": "✅ Payment received successfully! Your VIP access has been activated. Welcome!",
        "payment_success_no_plan": "✅ Payment received successfully! However, we could not identify the plan. Please contact support.",
        "payment_error_payload": "❌ Payment error: Invalid invoice payload.",
        "payment_error_unsupported_currency": "❌ Error: Currency not supported for this payment method.",
        "payment_error_pix_not_implemented": "❌ Error: Pix has not been implemented yet. Please use Stripe.",
        "payment_error": "❌ Error generating payment.",
        "payment_error_pix": "❌ Error generating Pix payment. Please try again.",
        "pix_invoice_title": "💎 Total VIP Access - Pix",
        "pix_invoice_description": "VIP access unlock ({label}) via Pix.",
        "pix_order_created": "✅ **Pix Order Created!**\n\nAmount: **{label}**\n\nScan the QR Code below or copy the Pix code to pay. After payment, click the button below to confirm.",
        "btn_pix_confirm": "✅ I Already Paid - Check Payment",
        "pix_scan_qr": "📱 **Scan the QR Code with your banking app or copy the Pix code above.**",
        "checking_payment": "🔍 Checking payment...",
        "payment_still_pending": "⏳ Payment still pending. Wait a few seconds and try again.",
        "payment_check_error": "❌ Error checking payment. Please try again in a moment.",
        "payment_not_found": "❌ Transaction not found. Please contact support.",
        
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
