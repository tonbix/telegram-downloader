#!/usr/bin/env bash

# Navigate to script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for .env file
if [ ! -f .env ]; then
    echo "[!] .env file not found."
    if [ -f .env.example ]; then
        echo "[*] Creating .env from .env.example..."
        cp .env.example .env
        echo "[!] Please edit .env with your API_ID and API_HASH before running again."
        exit 1
    fi
fi

# Check for virtual environment
if [ -d ".venv" ]; then
    PYTHON_BIN=".venv/bin/python"
else
    PYTHON_BIN="python3"
fi

echo "[*] Starting Telegram bot..."
exec "$PYTHON_BIN" main.py
