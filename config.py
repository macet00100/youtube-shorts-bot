import os
import json

# Storage paths
OUTPUT_DIR = "output"
ASSETS_DIR = "assets"
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
HISTORY_FILE = "data/history.json"
CREDS_FILE = "data/youtube_credentials.json"

# Load local credentials file if present
_saved_creds = {}
if os.path.exists(CREDS_FILE):
    try:
        with open(CREDS_FILE, "r", encoding="utf-8") as _f:
            _saved_creds = json.load(_f)
    except Exception:
        pass

# YouTube API Credentials (from GitHub Secrets or local file)
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", _saved_creds.get("YOUTUBE_CLIENT_ID", ""))
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", _saved_creds.get("YOUTUBE_CLIENT_SECRET", ""))
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", _saved_creds.get("YOUTUBE_REFRESH_TOKEN", ""))

# AI & Stock Media API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", _saved_creds.get("GEMINI_API_KEY", ""))
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", _saved_creds.get("PIXABAY_API_KEY", ""))

# Voice settings (International English voices: en-US-ChristopherNeural, en-US-GuyNeural)
# Christopher has a deep, mysterious, authoritative voice perfect for psychology & paradoxes
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "en-US-ChristopherNeural")

# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30
MAX_DURATION_SECONDS = 50

# Storage paths
OUTPUT_DIR = "output"
ASSETS_DIR = "assets"
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
HISTORY_FILE = "data/history.json"
