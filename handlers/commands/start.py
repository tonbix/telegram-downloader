import re
from telethon import TelegramClient, events
from core.config import COMMAND_PREFIX
from core.logger import logger

def register(client: TelegramClient):
    @client.on(events.NewMessage(pattern=rf'^{re.escape(COMMAND_PREFIX)}start(?:\s|$)'))
    async def start_handler(event):
        logger.info(f"Received {COMMAND_PREFIX}start command from user {event.sender_id}")
        await event.reply("hello! i am a downloader bot. I can download a lot of things like profile images, gifs, sticker packs, videos and all this has adjustable filters\noutput files can be saved to a local directory on your pc or sent back as attached archive")
