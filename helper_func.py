import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_SUB_CHANNELS, ADMINS, FORCE_SUB_MESSAGE, LOGGER
from database.database import db

async def is_subscribed(client, user_id):
    db_channels = await db.get_force_sub_channels()
    all_channels = list(set(FORCE_SUB_CHANNELS + db_channels))
    
    if not all_channels or all_channels == [0]:
        return True, []
    
    not_joined = []
    
    for channel_id in all_channels:
        try:
            member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status == "kicked":
                not_joined.append(channel_id)
        except UserNotParticipant:
            not_joined.append(channel_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error checking subscription for channel {channel_id}: {e}")
            not_joined.append(channel_id)
    
    return len(not_joined) == 0, not_joined

async def get_invite_links(client, channel_ids):
    links = []
    for channel_id in channel_ids:
        try:
            chat = await client.get_chat(channel_id)
            invite_link = chat.invite_link
            if not invite_link:
                invite_link = await client.export_chat_invite_link(channel_id)
            links.append((chat.title, invite_link))
        except Exception as e:
            LOGGER(__name__).error(f"Error getting invite link for {channel_id}: {e}")
    return links

async def handle_force_sub(client, message: Message):
    user_id = message.from_user.id
    subscribed, not_joined = await is_subscribed(client, user_id)
    
    if subscribed:
        return True
    
    invite_links = await get_invite_links(client, not_joined)
    
    buttons = []
    for idx, (channel_name, invite_link) in enumerate(invite_links, 1):
        buttons.append([InlineKeyboardButton(f"📢 Join {channel_name}", url=invite_link)])
    
    buttons.append([InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.username}?start=start")])
    
    text = FORCE_SUB_MESSAGE.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name or "",
        username=f"@{message.from_user.username}" if message.from_user.username else "None",
        mention=message.from_user.mention,
        id=message.from_user.id
    )
    
    await message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
    
    return False

def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").strip("=")

def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    return string_bytes.decode("ascii")

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temp_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temp_ids
            )
            total_messages += len(temp_ids)
            messages.extend(msgs)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            LOGGER(__name__).error(e)
            pass
    return messages

def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d '
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h '
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m '
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

def is_admin_filter():
    async def func(flt, client, message: Message):
        return message.from_user.id in ADMINS
    return filters.create(func)
