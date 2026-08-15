import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "downloader_session")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", ".")

# Proxy settings
PROXY_TYPE = os.getenv("PROXY_TYPE")
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")
PROXY_RDNS = os.getenv("PROXY_RDNS", "true").lower() in ("true", "1", "yes")
