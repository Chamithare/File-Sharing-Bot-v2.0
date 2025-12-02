from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from database.database import db
from config import CHANNEL_ID, DISABLE_CHANNEL_BUTTON, LOGGER
from helper_func import encode, is_admin_filter
import asyncio

@Client.on_message(filters.command('batch') & filters.private & is_admin_filter())
async def batch_command(client: Client, message: Message):
    """
    Create batch link for multiple files (SHORT category only)
    Usage: /batch
    Then forward first and last message from database channel
    """
    
    await message.reply_text(
        "📦 **Batch Link Generator**\n\n"
        "**Steps:**\n"
        "1️⃣ Forward the **first message** from SHORT database channel\n"
        "2️⃣ Forward the **last message** from SHORT database channel\n\n"
        "⚠️ Make sure both messages are from the SHORT database channel!\n"
        "⚠️ Batch links are for SHORT category only (auto-delete)."
    )
    
    # Store user state for batch creation
    client.batch_states = getattr(client, 'batch_states', {})
    client.batch_states[message.from_user.id] = {'step': 1, 'first_id': None}

@Client.on_message(filters.private & filters.forwarded & is_admin_filter())
async def handle_batch_forward(client: Client, message: Message):
    """Handle forwarded messages for batch creation"""
    
    # Check if user is in batch creation mode
    batch_states = getattr(client, 'batch_states', {})
    user_id = message.from_user.id
    
    if user_id not in batch_states:
        return
    
    state = batch_states[user_id]
    
    # Verify message is from SHORT database channel
    if message.forward_from_chat.id != CHANNEL_ID:
        await message.reply_text(
            "❌ This message is not from the SHORT database channel!\n"
            "Please forward messages from the correct channel."
        )
        return
    
    if state['step'] == 1:
        # First message received
        state['first_id'] = message.forward_from_message_id
        state['step'] = 2
        
        await message.reply_text(
            f"✅ First message ID: `{state['first_id']}`\n\n"
            "Now forward the **last message** from the SHORT database channel."
        )
    
    elif state['step'] == 2:
        # Last message received
        last_id = message.forward_from_message_id
        first_id = state['first_id']
        
        # Validate range
        if last_id < first_id:
            await message.reply_text(
                "❌ Last message ID must be greater than first message ID!\n"
                "Please start over with `/batch`"
            )
            del batch_states[user_id]
            return
        
        # Check range size
        total_files = last_id - first_id + 1
        if total_files > 100:
            await message.reply_text(
                f"❌ Batch too large! ({total_files} files)\n"
                "Maximum batch size is 100 files.\n"
                "Please select a smaller range."
            )
            del batch_states[user_id]
            return
        
        # Generate batch link
        batch_string = f"{first_id}-{last_id}"
        base64_string = encode(batch_string)
        link = f"https://t.me/{client.username}?start={base64_string}"
        
        # Create reply markup
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔗 Share Batch Link", url=f'https://t.me/share/url?url={link}')]]
        ) if not DISABLE_CHANNEL_BUTTON else None
        
        # Send batch link
        await message.reply_text(
            f"✅ **Batch Link Created!**\n\n"
            f"📊 Range: {first_id} to {last_id}\n"
            f"📦 Total Files: {total_files}\n"
            f"🔗 Link: `{link}`\n\n"
            f"⚠️ This is a SHORT category batch (auto-delete enabled)",
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        
        LOGGER(__name__).info(f"Batch created by admin {user_id}: {first_id}-{last_id}")
        
        # Clear state
        del batch_states[user_id]

@Client.on_message(filters.command('genlink') & filters.private & is_admin_filter())
async def genlink_command(client: Client, message: Message):
    """
    Generate link for a single message
    Usage: /genlink
    Then forward message from database channel
    """
    
    await message.reply_text(
        "🔗 **Single Link Generator**\n\n"
        "Forward a message from any database channel (SHORT or MOVIE).\n\n"
        "• From SHORT channel = Auto-delete link\n"
        "• From MOVIE channel = Permanent link"
    )
    
    # Store user state
    client.genlink_states = getattr(client, 'genlink_states', {})
    client.genlink_states[message.from_user.id] = True

@Client.on_message(filters.private & filters.forwarded & is_admin_filter())
async def handle_genlink_forward(client: Client, message: Message):
    """Handle forwarded message for single link generation"""
    
    # Check if user is in genlink mode
    genlink_states = getattr(client, 'genlink_states', {})
    user_id = message.from_user.id
    
    if user_id not in genlink_states:
        return
    
    from config import MOVIE_CHANNEL_ID
    
    # Determine which channel
    channel_id = message.forward_from_chat.id
    
    if channel_id == CHANNEL_ID:
        category = "short"
        category_text = "SHORT (Auto-Delete)"
    elif channel_id == MOVIE_CHANNEL_ID:
        category = "movie"
        category_text = "MOVIE (Permanent)"
    else:
        await message.reply_text(
            "❌ This message is not from a recognized database channel!\n"
            "Please forward from SHORT or MOVIE database channel."
        )
        del genlink_states[user_id]
        return
    
    # Get message ID
    msg_id = message.forward_from_message_id
    
    # Verify file exists in database
    file_data = await db.get_file(msg_id)
    
    if not file_data:
        await message.reply_text(
            "⚠️ File not found in database. It may not have been processed yet.\n"
            "Wait a few seconds and try again."
        )
        del genlink_states[user_id]
        return
    
    # Generate link
    base64_string = encode(str(msg_id))
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    # Create reply markup
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔗 Share Link", url=f'https://t.me/share/url?url={link}')]]
    ) if not DISABLE_CHANNEL_BUTTON else None
    
    # Send link
    await message.reply_text(
        f"✅ **Link Generated!**\n\n"
        f"📁 Category: {category_text}\n"
        f"🔢 Message ID: `{msg_id}`\n"
        f"🔗 Link: `{link}`",
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    
    LOGGER(__name__).info(f"Single link generated by admin {user_id}: {msg_id} ({category})")
    
    # Clear state
    del genlink_states[user_id]