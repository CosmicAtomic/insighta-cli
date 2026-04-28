import os
import json
from pathlib import Path

CREDENTIALS_DIR = Path.home() / ".insighta"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"

def save_tokens(access_token, refresh_token):
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(tokens, f, indent=4)

def load_tokens():
    if not CREDENTIALS_FILE.exists():
        return None
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def clear_tokens():
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()
