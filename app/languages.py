
"""
Multi-language support module - v8.0 Ultra
Provides high-conversion translations for PT, ES, and EN
"""

from typing import Dict, Any

TRANSLATIONS = {
    "pt": {
        # Welcome & Selection
        "select_lang": "🌐 **Selecione seu idioma / Select your language / Seleccione su idioma**",
        "welcome_title": "🔥 **BEM-VINDO AO PARAÍSO VIP, {name}!** 🔥",
        "welcome_copy": (
            "Você acaba de entrar no bot de mídias mais exclusivo do Telegram. 🔞\n\n"
            "🚀 **O QUE VOCÊ PODE FAZER AGORA:**\n"
            "• Buscar suas modelos favoritas do OnlyFans/Privacy\n"
            "• Receber prévias picantes direto no seu PV\n"
            "• Acessar packs completos sem censura no VIP\n\n"
            "💎 **Não perca tempo, o conteúdo que você deseja está a um clique de distância.**"
        ),
        
        # Menu Buttons
        "btn_search": "🔍 Buscar Modelo",
        "btn_vip": "💎 Assinar VIP",
        "btn_help": "❓ Ajuda",
        "btn_lang": "🌐 Idioma",
        "btn_stats": "📊 Minha Conta",
        "btn_share": "🎁 Ganhar Mídias Grátis",
        "btn_god_mode": "⚡ MODO GOD: {status}",
        
        # Referral System
        "referral_title": "🎁 **GANHE MÍDIAS COMPLETAS GRÁTIS!**",
        "referral_copy": (
            "Convide amigos para o bot e ganhe recompensas:\n\n"
            "✅ Cada amigo que entrar pelo seu link libera **3 mídias completas** para você!\n\n"
            "🔗 **Seu Link Único:**\n`{link}`\n\n"
            "👥 **Estatísticas:**\n"
            "• Amigos convidados: {count}\n"
            "• Créditos disponíveis: {credits}\n\n"
            "📢 **DICA:** Compartilhe em grupos ativos para ganhar mais rápido!"
        ),
        "referral_reward_msg": "🎉 **Parabéns!** Um amigo entrou pelo seu link. Você ganhou **3 créditos** para ver mídias completas!",
        
        # Search Flow
        "search_prompt": "✍️ **Digite o nome da modelo que você deseja encontrar:**",
        "searching": "🔍 Vasculhando os arquivos secretos de **{name}**...",
        "no_media_found": "❌ **{name}** ainda não está em nosso banco de dados. Tente outro nome!",
        "select_model": "✅ Encontramos essas beldades. Qual você quer ver?",
        
        # Payment/VIP Flow
        "vip_offer_title": "🔞 **ACESSO TOTAL LIBERADO!**",
        "vip_offer_copy": (
            "Pare de ver apenas prévias. Tenha o conteúdo **COMPLETO** e **SEM CENSURA** agora mesmo!\n\n"
            "✨ **Vantagens VIP:**\n"
            "• Download ilimitado de fotos e vídeos\n"
            "• Qualidade 4K Ultra HD\n"
            "• Atualizações automáticas diárias\n\n"
            "👇 **Escolha seu plano e domine o acesso:**"
        ),
        "downsell_title": "🎁 **ESPERA! UMA ÚLTIMA TENTATIVA...**",
        "downsell_copy": "Vi que você hesitou. Liberei um **Plano Especial** com 30% de desconto para você entrar no VIP agora! Não deixe essa chance passar. 😱",
        
        # God Mode
        "god_mode_on": "Ativado 🟢",
        "god_mode_off": "Desativado 🔴",
        "god_mode_msg": "⚡ **MODO GOD ALTERNADO:** Agora você está operando como **{mode}**.",
        
        # Other
        "error_occurred": "❌ Ops! Algo deu errado: {error}",
        "search_usage": "❌ Digite o nome da modelo após o comando ou use o botão de busca.",
        "loading": "🔄 Carregando...",
        "using_credit": "🎫 **Usando 1 crédito de indicação para liberar esta mídia...**",
    },
    
    "es": {
        # Welcome & Selection
        "select_lang": "🌐 **Seleccione su idioma**",
        "welcome_title": "🔥 **¡BIENVENIDO AL PARAÍSO VIP, {name}!** 🔥",
        "welcome_copy": (
            "Acabas de entrar al bot de medios más exclusivo de Telegram. 🔞\n\n"
            "🚀 **QUÉ PUEDES HACER AHORA:**\n"
            "• Buscar tus modelos favoritas de OnlyFans/Coomer\n"
            "• Recibir vistas previas picantes directo en tu chat\n"
            "• Acceder a packs completos sin censura en el VIP\n\n"
            "💎 **No pierdas tiempo, el contenido que deseas está a un solo clic.**"
        ),
        
        # Menu Buttons
        "btn_search": "🔍 Buscar Modelo",
        "btn_vip": "💎 Suscribirse VIP",
        "btn_help": "❓ Ayuda",
        "btn_lang": "🌐 Idioma",
        "btn_stats": "📊 Mi Cuenta",
        "btn_share": "🎁 Ganar Medios Gratis",
        "btn_god_mode": "⚡ MODO GOD: {status}",
        
        # Referral System
        "referral_title": "🎁 **¡GANA MEDIOS COMPLETOS GRATIS!**",
        "referral_copy": (
            "Invita amigos al bot y gana recompensas:\n\n"
            "✅ ¡Cada amigo que entre por tu enlace libera **3 medios completos** para ti!\n\n"
            "🔗 **Tu Enlace Único:**\n`{link}`\n\n"
            "👥 **Estadísticas:**\n"
            "• Amigos invitados: {count}\n"
            "• Créditos disponibles: {credits}\n\n"
            "📢 **CONSEJO:** ¡Comparte en grupos activos para ganar más rápido!"
        ),
        "referral_reward_msg": "🎉 **¡Felicidades!** Un amigo entró por tu enlace. ¡Has ganado **3 créditos** para ver medios completos!",
        
        # Search Flow
        "search_prompt": "✍️ **Escribe el nombre de la modelo que deseas encontrar:**",
        "searching": "🔍 Buscando en los archivos secretos de **{name}**...",
        "no_media_found": "❌ **{name}** aún no está en nuestra base de datos. ¡Intenta con otro nombre!",
        "select_model": "✅ Encontramos estas bellezas. ¿A cuál quieres ver?",
        
        # Payment/VIP Flow
        "vip_offer_title": "🔞 **¡ACCESO TOTAL LIBERADO!**",
        "vip_offer_copy": (
            "Deja de ver solo vistas previas. ¡Ten el contenido **COMPLETO** y **SIN CENSURA** ahora mismo!\n\n"
            "✨ **Ventajas VIP:**\n"
            "• Descarga ilimitada de fotos y videos\n"
            "• Calidad 4K Ultra HD\n"
            "• Actualizaciones automáticas diarias\n\n"
            "👇 **Elige tu plan y domina el acceso:**"
        ),
        "downsell_title": "🎁 **¡ESPERA! UN ÚLTIMO INTENTO...**",
        "downsell_copy": "Vi que dudaste. ¡He liberado un **Plan Especial** con 30% de descuento para que entres al VIP ahora! No dejes pasar esta oportunidad. 😱",
        
        # God Mode
        "god_mode_on": "Activado 🟢",
        "god_mode_off": "Desactivado 🔴",
        "god_mode_msg": "⚡ **MODO GOD ALTERNADO:** Ahora estás operando como **{mode}**.",
        
        # Other
        "error_occurred": "❌ ¡Ops! Algo salió mal: {error}",
        "search_usage": "❌ Escribe el nombre de la modelo después del comando o usa el botón de búsqueda.",
        "loading": "🔄 Cargando...",
        "using_credit": "🎫 **Usando 1 crédito de invitación para liberar este medio...**",
    },
    
    "en": {
        # Welcome & Selection
        "select_lang": "🌐 **Select your language**",
        "welcome_title": "🔥 **WELCOME TO VIP PARADISE, {name}!** 🔥",
        "welcome_copy": (
            "You have just entered the most exclusive media bot on Telegram. 🔞\n\n"
            "🚀 **WHAT YOU CAN DO NOW:**\n"
            "• Search for your favorite OnlyFans/Coomer models\n"
            "• Receive spicy previews directly in your DM\n"
            "• Access full uncensored packs in VIP\n\n"
            "💎 **Don't waste time, the content you desire is just one click away.**"
        ),
        
        # Menu Buttons
        "btn_search": "🔍 Search Model",
        "btn_vip": "💎 Subscribe VIP",
        "btn_help": "❓ Help",
        "btn_lang": "🌐 Language",
        "btn_stats": "📊 My Account",
        "btn_share": "🎁 Get Free Media",
        "btn_god_mode": "⚡ GOD MODE: {status}",
        
        # Referral System
        "referral_title": "🎁 **GET FREE FULL MEDIA!**",
        "referral_copy": (
            "Invite friends to the bot and earn rewards:\n\n"
            "✅ Every friend who joins via your link unlocks **3 full media** for you!\n\n"
            "🔗 **Your Unique Link:**\n`{link}`\n\n"
            "👥 **Stats:**\n"
            "• Friends invited: {count}\n"
            "• Available credits: {credits}\n\n"
            "📢 **TIP:** Share in active groups to earn faster!"
        ),
        "referral_reward_msg": "🎉 **Congratulations!** A friend joined through your link. You earned **3 credits** to view full media!",
        
        # Search Flow
        "search_prompt": "✍️ **Type the name of the model you want to find:**",
        "searching": "🔍 Searching through the secret archives of **{name}**...",
        "no_media_found": "❌ **{name}** is not in our database yet. Try another name!",
        "select_model": "✅ We found these beauties. Which one do you want to see?",
        
        # Payment/VIP Flow
        "vip_offer_title": "🔞 **FULL ACCESS UNLOCKED!**",
        "vip_offer_copy": (
            "Stop watching just previews. Get the **FULL** and **UNCENSORED** content right now!\n\n"
            "✨ **VIP Advantages:**\n"
            "• Unlimited photo and video downloads\n"
            "• 4K Ultra HD quality\n"
            "• Daily automatic updates\n\n"
            "👇 **Choose your plan and dominate access:**"
        ),
        "downsell_title": "🎁 **WAIT! ONE LAST ATTEMPT...**",
        "downsell_copy": "I saw you hesitated. I've unlocked a **Special Plan** with 30% discount for you to join VIP now! Don't let this chance slip away. 😱",
        
        # God Mode
        "god_mode_on": "Enabled 🟢",
        "god_mode_off": "Disabled 🔴",
        "god_mode_msg": "⚡ **GOD MODE TOGGLED:** You are now operating as **{mode}**.",
        
        # Other
        "error_occurred": "❌ Oops! Something went wrong: {error}",
        "search_usage": "❌ Type the model name after the command or use the search button.",
        "loading": "🔄 Loading...",
        "using_credit": "🎫 **Using 1 referral credit to unlock this media...**",
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
