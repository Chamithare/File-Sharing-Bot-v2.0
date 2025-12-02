import os
import logging
from logging.handlers import RotatingFileHandler

# Bot information
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Database channels - IMPORTANT!
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "0"))  # Short videos DB (AUTO-DELETE)
MOVIE_CHANNEL_ID = int(os.environ.get("MOVIE_CHANNEL_ID", "0"))  # Movie DB (PERMANENT)

# Owner and admins
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
ADMINS = []
admin_ids = os.environ.get("ADMINS", "")
if admin_ids:
    for admin_id in admin_ids.split():
        ADMINS.append(int(admin_id))
if OWNER_ID not in ADMINS:
    ADMINS.append(OWNER_ID)

# Database
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "filesharexbot")

# Multiple Force Subscribe Channels (comma-separated)
FORCE_SUB_CHANNELS = os.environ.get("FORCE_SUB_CHANNELS", "0")
# Convert to list of integers
if FORCE_SUB_CHANNELS:
    FORCE_SUB_CHANNELS = [int(x.strip()) for x in FORCE_SUB_CHANNELS.split(",") if x.strip() and x.strip() != "0"]
else:
    FORCE_SUB_CHANNELS = []

# Protect content
PROTECT_CONTENT = os.environ.get("PROTECT_CONTENT", "False").lower() == "true"

# Auto-delete settings
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "25200"))  # 7 hours default
AUTO_DELETE_MSG = os.environ.get("AUTO_DELETE_MSG", 
    "⚠️ <b>This file will be automatically deleted in {time} seconds.</b>\n\n"
    "📥 Please save it now!"
)
AUTO_DEL_SUCCESS_MSG = os.environ.get("AUTO_DEL_SUCCESS_MSG",
    "✅ File deleted successfully after the specified time."
)

# Start message
START_MESSAGE = os.environ.get("START_MESSAGE",
    "Hello {first}\n\n"
    "I can store private files in a specified channel and other users can access them from a special link."
)

# Start picture
START_PIC = os.environ.get("START_PIC", "")

# Force subscribe message
FORCE_SUB_MESSAGE = os.environ.get("FORCE_SUB_MESSAGE",
    "Hello {first}\n\n"
    "🔒 <b>You must join our channel(s) to use this bot!</b>\n\n"
    "📢 Please join the channel(s) below and try again:"
)

# Custom caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "")

# Channel button
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", "False").lower() == "true"

# Bot stats text
BOT_STATS_TEXT = os.environ.get("BOT_STATS_TEXT",
    "<b>BOT UPTIME</b>\n{uptime}"
)

# User reply text
USER_REPLY_TEXT = os.environ.get("USER_REPLY_TEXT",
    "❌ You are not authorized to use this command."
)

# Join request
JOIN_REQUEST_ENABLED = os.environ.get("JOIN_REQUEST_ENABLED", "False").lower() == "true"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            "log.txt",
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)