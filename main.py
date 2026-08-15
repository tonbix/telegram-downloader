import asyncio
from core.client import get_client
from core.logger import logger
from handlers.router import register_handlers

async def main():
    logger.info("Starting application...")
    client = get_client()
    
    # Register all modular handlers
    register_handlers(client)
    
    # Start the client
    # If the session is new, Telethon will prompt for phone number and verification code in the terminal.
    logger.info("Starting client authentication...")
    await client.start()
    
    logger.info("Client is running. Press Ctrl+C to stop.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped manually.")
    except Exception as e:
        logger.exception("A critical error occurred.")
