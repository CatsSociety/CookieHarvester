# transport/__init__.py
# Selector de transporte según config.TRANSPORT_ACTIVO.

from config import (
    TRANSPORT_ACTIVO,
    DISCORD_WEBHOOK_URL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)

from .discord import DiscordTransport
from .telegram import TelegramTransport


def get_transport():
    """
    Devuelve la instancia de transporte configurada en el .env.
    Por defecto: Discord.
    """
    if TRANSPORT_ACTIVO == "discord":
        print("[DEBUG] Transporte seleccionado: Discord")
        return DiscordTransport(DISCORD_WEBHOOK_URL)
    elif TRANSPORT_ACTIVO == "telegram":
        print("[DEBUG] Transporte seleccionado: Telegram")
        return TelegramTransport(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    else:
        raise ValueError(f"Transporte desconocido: {TRANSPORT_ACTIVO}")