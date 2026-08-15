import re
from pathlib import Path
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetSavedGifsRequest
from telethon.tl.types import DocumentAttributeAnimated
from core.config import COMMAND_PREFIX
from core.logger import logger
from core.utils import get_downloads_dir, convert_mp4_to_gif


def register(client: TelegramClient):
    pattern = rf"^{re.escape(COMMAND_PREFIX)}(?:download_gifs|downloadgifs|gifs)(?:\s|$)"

    @client.on(events.NewMessage(pattern=pattern))
    async def download_gifs_handler(event):
        status_msg = await event.reply("searching for gifs in account...")
        logger.info(f"Triggered GIF download command by user {event.sender_id}")

        try:
            download_dir = get_downloads_dir("Telegram_GIFs")
            download_dir.mkdir(parents=True, exist_ok=True)

            gifs_to_download = []
            seen_ids = set()

            # 1. Fetch from Telegram's Saved GIFs tab
            try:
                result = await client(GetSavedGifsRequest(hash=0))
                if hasattr(result, "gifs") and result.gifs:
                    for gif in result.gifs:
                        if gif.id not in seen_ids:
                            seen_ids.add(gif.id)
                            gifs_to_download.append(gif)
            except Exception as e:
                logger.warning(f"Failed to fetch Saved GIFs tab: {e}")

            # 2. Fetch animated GIFs from Saved Messages chat ('me')
            try:
                async for msg in client.iter_messages("me", limit=300):
                    if msg.document:
                        is_gif = (
                            msg.document.mime_type in ("image/gif", "video/mp4")
                            and any(
                                isinstance(attr, DocumentAttributeAnimated)
                                for attr in msg.document.attributes
                            )
                        ) or msg.document.mime_type == "image/gif"

                        if is_gif and msg.document.id not in seen_ids:
                            seen_ids.add(msg.document.id)
                            gifs_to_download.append(msg.document)
            except Exception as e:
                logger.warning(f"Failed to scan Saved Messages for GIFs: {e}")

            total_gifs = len(gifs_to_download)
            if total_gifs == 0:
                await status_msg.edit("no saved gifs found in account.")
                return

            await status_msg.edit(
                f"found {total_gifs} gifs, starting download to {download_dir}"
            )

            successful = 0
            failed = 0

            for idx, gif_doc in enumerate(gifs_to_download, start=1):
                try:
                    saved_file = await client.download_media(gif_doc, file=download_dir)
                    if saved_file:
                        saved_path = Path(saved_file)
                        if saved_path.suffix.lower() == ".mp4":
                            await convert_mp4_to_gif(saved_path, delete_original=True)
                    successful += 1

                    if idx % 5 == 0 or idx == total_gifs:
                        err_str = f" (errors:{failed})" if failed > 0 else ""
                        await status_msg.edit(
                            f"downloading your gifs: {idx}/{total_gifs}{err_str}"
                        )
                except Exception as e:
                    logger.error(f"Failed to download GIF ID {gif_doc.id}: {e}")
                    failed += 1

            err_str = f" (errors:{failed})" if failed > 0 else ""
            await status_msg.edit(
                f"downloaded {successful}/{total_gifs} gifs to {download_dir}{err_str}"
            )

        except Exception as e:
            logger.exception("Error while downloading GIFs")
            await status_msg.edit(f"an error occurred: {e}")
