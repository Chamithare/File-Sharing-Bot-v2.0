from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserNotParticipant
from database.database import db
from config import (
    START_MESSAGE, START_PIC, CHANNEL_ID, MOVIE_CHANNEL_ID,
    PROTECT_CONTENT, AUTO_DELETE_TIME, AUTO_DELETE_MSG,
    AUTO_DEL_SUCCESS_MSG, CUSTOM_CAPTION, LOGGER
)
from helper_func import decode, handle_force_sub, get_readable_time
import asyncio

@Client.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    
    # Add user to database
    await db.add_user(
        user_id,
        first_name=message.from_user.first_name,
        username=message.from_user.username
    )
    
    # Check if it's a file request (has base64 parameter)
    if len(message.text) > 7:
        # Extract base64 from command
        base64_string = message.text.split(" ", 1)[1]
        
        try:
            # Decode to get message ID
            string = decode(base64_string)
            
            # Check for batch (contains "-")
            if "-" in string:
                # Batch request
                await handle_batch_request(client, message, string)
            else:
                # Single file request
                await handle_file_request(client, message, int(string))
        
        except Exception as e:
            LOGGER(__name__).error(f"Error decoding link: {e}")
            await message.reply_text("❌ Invalid or expired link!")
        
        return
    
    # Regular start message (no file request)
    text = START_MESSAGE.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name or "",
        username=f"@{message.from_user.username}" if message.from_user.username else "None",
        mention=message.from_user.mention,
        id=message.from_user.id
    )
    
    if START_PIC:
        await message.reply_photo(
            photo=START_PIC,
            caption=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("ℹ️ About", callback_data="about"),
                  InlineKeyboardButton("🆘 Help", callback_data="help")]]
            )
        )
    else:
        await message.reply_text(
            text=text,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("ℹ️ About", callback_data="about"),
                  InlineKeyboardButton("🆘 Help", callback_data="help")]]
            )
        )

async def handle_file_request(client: Client, message: Message, file_id: int):
    """Handle single file request"""
    user_id = message.from_user.id
    
    # Check force subscribe
    subscribed = await handle_force_sub(client, message)
    if not subscribed:
        return
    
    # Get file from database
    file_data = await db.get_file(file_id)
    
    if not file_data:
        await message.reply_text("❌ File not found or has been deleted!")
        return
    
    # Determine which channel to get file from
    category = file_data.get("category", "short")
    channel_id = MOVIE_CHANNEL_ID if category == "movie" else CHANNEL_ID
    
    try:
        # Get the message from database channel
        msg = await client.get_messages(chat_id=channel_id, message_ids=file_id)
        
        # Prepare caption
        caption = CUSTOM_CAPTION.format(
            filename=getattr(msg.document, "file_name", ""),
            previouscaption=msg.caption.html if msg.caption else "",
            file_size=getattr(msg.document, "file_size", ""),
        ) if CUSTOM_CAPTION and msg.document else (msg.caption.html if msg.caption else "")
        
        # Check if auto-delete is enabled for this category
        auto_delete_enabled = (category == "short" and AUTO_DELETE_TIME)
        
        # Add auto-delete warning to caption
        if auto_delete_enabled:
            delete_time = get_readable_time(AUTO_DELETE_TIME)
            warning = AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
            caption = f"{caption}\n\n{warning}" if caption else warning
        
        # Copy the message to user
        sent_message = await msg.copy(
            chat_id=user_id,
            caption=caption,
            protect_content=PROTECT_CONTENT,
            reply_markup=msg.reply_markup
        )
        
        LOGGER(__name__).info(f"File {file_id} sent to user {user_id} (category: {category})")
        
        # Schedule auto-delete if enabled
        if auto_delete_enabled:
            asyncio.create_task(delete_file_after_time(client, sent_message, user_id))
    
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await handle_file_request(client, message, file_id)
    except Exception as e:
        LOGGER(__name__).error(f"Error sending file: {e}")
        await message.reply_text("❌ Error retrieving file. Please try again later.")

async def handle_batch_request(client: Client, message: Message, batch_string: str):
    """Handle batch file request"""
    user_id = message.from_user.id
    
    # Check force subscribe
    subscribed = await handle_force_sub(client, message)
    if not subscribed:
        return
    
    try:
        # Parse batch string (format: "first_id-last_id")
        first_id, last_id = map(int, batch_string.split("-"))
        
        # Limit batch size
        if (last_id - first_id) > 100:
            await message.reply_text("❌ Batch size too large! Maximum 100 files at once.")
            return
        
        await message.reply_text("📦 Sending batch files... Please wait.")
        
        # Send all files in batch
        for msg_id in range(first_id, last_id + 1):
            try:
                # Get file from database
                file_data = await db.get_file(msg_id)
                
                if not file_data:
                    continue
                
                # Get category (batch is always from SHORT channel)
                category = file_data.get("category", "short")
                channel_id = CHANNEL_ID  # Batch is always short
                
                # Get message
                msg = await client.get_messages(chat_id=channel_id, message_ids=msg_id)
                
                # Prepare caption with auto-delete warning
                caption = msg.caption.html if msg.caption else ""
                if AUTO_DELETE_TIME and category == "short":
                    warning = AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
                    caption = f"{caption}\n\n{warning}" if caption else warning
                
                # Send file
                sent_message = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    protect_content=PROTECT_CONTENT
                )
                
                # Schedule auto-delete if enabled
                if AUTO_DELETE_TIME and category == "short":
                    asyncio.create_task(delete_file_after_time(client, sent_message, user_id))
                
                await asyncio.sleep(1)  # Avoid flood
            
            except Exception as e:
                LOGGER(__name__).error(f"Error in batch file {msg_id}: {e}")
                continue
        
        await message.reply_text("✅ All available files sent!")
        
    except Exception as e:
        LOGGER(__name__).error(f"Error in batch request: {e}")
        await message.reply_text("❌ Error processing batch request!")

async def delete_file_after_time(client: Client, message: Message, user_id: int):
    """Delete file after specified time"""
    try:
        await asyncio.sleep(AUTO_DELETE_TIME)
        
        # Delete the message
        await client.delete_messages(chat_id=user_id, message_ids=message.id)
        
        # Send success message
        await client.send_message(
            chat_id=user_id,
            text=AUTO_DEL_SUCCESS_MSG
        )
        
        LOGGER(__name__).info(f"File auto-deleted for user {user_id}")
    
    except Exception as e:
        LOGGER(__name__).error(f"Error auto-deleting file: {e}")

@Client.on_callback_query(filters.regex("^(about|help)$"))
async def callback_handler(client: Client, callback: CallbackQuery):
    """Handle callback queries for buttons"""
    data = callback.data
    
    if data == "about":
        await callback.answer()
        await callback.message.edit_text(
            "🤖 **About This Bot**\n\n"
            "This bot can store files and generate shareable links.\n\n"
            "📦 **Features:**\n"
            "• Auto-delete for short videos (configurable)\n"
            "• Permanent links for movies\n"
            "• Multiple force subscribe channels\n"
            "• Batch file sharing\n\n"
            "Powered by Pyrogram",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="start")]]
            )
        )
    
    elif data == "help":
        await callback.answer()
        await callback.message.edit_text(
            "🆘 **Help**\n\n"
            "**For Users:**\n"
            "• Click on shared links to get files\n"
            "• Join required channels to access files\n\n"
            "**For Admins:**\n"
            "• Send files to Short DB: Auto-delete\n"
            "• Send files to Movie DB: Permanent\n"
            "• Use /batch for batch links\n"
            "• Use /settings for admin panel",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="start")]]
            )
        )
    
    elif data == "start":
        await callback.answer()
        text = START_MESSAGE.format(
            first=callback.from_user.first_name,
            last=callback.from_user.last_name or "",
            username=f"@{callback.from_user.username}" if callback.from_user.username else "None",
            mention=callback.from_user.mention,
            id=callback.from_user.id
        )
        await callback.message.edit_text(
            text=text,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("ℹ️ About", callback_data="about"),
                  InlineKeyboardButton("🆘 Help", callback_data="help")]]
            )
        )