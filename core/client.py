import socks
from telethon import TelegramClient
from core.config import (
    API_ID,
    API_HASH,
    SESSION_NAME,
    PROXY_TYPE,
    PROXY_HOST,
    PROXY_PORT,
    PROXY_USER,
    PROXY_PASS,
    PROXY_RDNS,
)
from core.logger import logger


def get_proxy():
    if not PROXY_HOST or not PROXY_PORT or not PROXY_TYPE:
        return None

    proxy_type_upper = PROXY_TYPE.upper()
    type_map = {
        "SOCKS5": socks.SOCKS5,
        "SOCKS4": socks.SOCKS4,
        "HTTP": socks.HTTP,
    }

    if proxy_type_upper not in type_map:
        logger.warning(f"Unsupported PROXY_TYPE '{PROXY_TYPE}'. Proxy disabled.")
        return None

    try:
        port = int(PROXY_PORT)
    except ValueError:
        logger.error(f"Invalid PROXY_PORT '{PROXY_PORT}'. Proxy disabled.")
        return None

    return (
        type_map[proxy_type_upper],
        PROXY_HOST,
        port,
        PROXY_RDNS,
        PROXY_USER if PROXY_USER else None,
        PROXY_PASS if PROXY_PASS else None,
    )


def get_client() -> TelegramClient:
    if not API_ID or not API_HASH:
        logger.error("API_ID and API_HASH must be set in the .env file")
        raise ValueError("API_ID and API_HASH are missing.")

    logger.info(f"Initializing Telegram client with session: {SESSION_NAME}")
    proxy = get_proxy()
    if proxy:
        logger.info(f"Using {PROXY_TYPE} proxy at {PROXY_HOST}:{PROXY_PORT}")

    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH, proxy=proxy)
    return client
