import importlib
import pkgutil
from telethon import TelegramClient
from core.logger import logger
import handlers.commands

def register_handlers(client: TelegramClient):
    """
    Dynamically loads and registers all modules in the handlers.commands package.
    Each module should have a 'register(client)' function.
    """
    logger.info("Registering handlers...")
    
    package = handlers.commands
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_module_name = f"{package.__name__}.{module_name}"
        module = importlib.import_module(full_module_name)
        
        if hasattr(module, 'register'):
            module.register(client)
            logger.info(f"Registered handler: {module_name}")
        else:
            logger.warning(f"Module {module_name} does not have a 'register' function.")
