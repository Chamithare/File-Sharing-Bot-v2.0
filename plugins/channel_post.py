from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from database.database import db
from config import CHANNEL_ID, MOVIE_CHANNEL_ID, ADMINS, DISABLE_CHANNEL_BUTTON, LOGGER
from helper_func import encode
import asyncio

# Handle posts in SHORT database channel (auto-delete category)
@Client.on_message(filters.channel & filters.chat(CHANNEL_ID) & ~filters.edited)
async def handle_short_channel_post(client: Client, message: Message):
    """Handle posts in SHORT database channel - auto-delete category"""
    try:
        # Store file with "short" category
        await db.add_file(message.id, message.id, category="short")
        
        # Generate shareable link
        base64_string = encode(f"{message.id}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        # Create reply markup
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔗 Share Link", url=f'https://t.me/share/url?url={link}')]]
        ) if not DISABLE_CHANNEL_BUTTON else None
        
        # Reply with link in the channel
        await message.reply_text(
            text=f"📦 **Short File Link (Auto-Delete)**\n\n"
                 f"🔗 Link: `{link}`\n\n"
                 f"⚠️ This file will be auto-deleted after the set time.",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        
        LOGGER(__name__).info(f"Short file added: {message.id}")
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await handle_short_channel_post(client, message)
    except Exception as e:
        LOGGER(__name__).error(f"Error in short channel handler: {e}")

# Handle posts in MOVIE database channel (permanent category)
@Client.on_message(filters.channel & filters.chat(MOVIE_CHANNEL_ID) & ~filters.edited)
async def handle_movie_channel_post(client: Client, message: Message):
    """Handle posts in MOVIE database channel - permanent category"""
    try:
        # Store file with "movie" category (permanent)
        await db.add_file(message.id, message.id, category="movie")
        
        # Generate shareable link
        base64_string = encode(f"{message.id}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        # Create reply markup
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔗 Share Link", url=f'https://t.me/share/url?url={link}')]]
        ) if not DISABLE_CHANNEL_BUTTON else None
        
        # Reply with link in the channel
        await message.reply_text(
            text=f"🎬 **Movie File Link (Permanent)**\n\n"
                 f"🔗 Link: `{link}`\n\n"
                 f"✅ This file will NOT be deleted automatically.",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        
        LOGGER(__name__).info(f"Movie file added: {message.id}")
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await handle_movie_channel_post(client, message)
    except Exception as e:
        LOGGER(__name__).error(f"Error in movie channel handler: {e}")

# Handle direct messages to bot (forward to SHORT channel)
@Client.on_message(filters.private & filters.create(lambda _, __, m: m.from_user.id in ADMINS) & (filters.document | filters.video | filters.audio))
async def handle_direct_upload(client: Client, message: Message):
    """Handle files sent directly to bot - forward to SHORT channel"""
    try:
        # Forward to SHORT database channel
        forwarded = await message.forward(CHANNEL_ID)
        
        # Store with "short" category
        await db.add_file(forwarded.id, forwarded.id, category="short")
        
        # Generate link
        base64_string = encode(f"{forwarded.id}")
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        # Reply to admin
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔗 Share Link", url=f'https://t.me/share/url?url={link}')]]
        ) if not DISABLE_CHANNEL_BUTTON else None
        
        await message.reply_text(
            text=f"✅ **File uploaded to SHORT database!**\n\n"
                 f"🔗 Link: `{link}`\n\n"
                 f"⚠️ Auto-delete enabled\n"
                 f"📝 To create permanent movie links, send to Movie DB channel.",
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        
        LOGGER(__name__).info(f"Direct upload forwarded to SHORT: {forwarded.id}")
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await handle_direct_upload(client, message)
    except Exception as e:
        LOGGER(__name__).error(f"Error in direct upload handler: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")
