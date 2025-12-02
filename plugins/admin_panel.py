from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import db
from config import ADMINS, AUTO_DELETE_TIME, LOGGER
from helper_func import is_admin_filter, get_readable_time

@Client.on_message(filters.command('settings') & filters.private & is_admin_filter())
async def settings_command(client: Client, message: Message):
    """Admin panel - main settings menu"""
    
    # Get current settings
    force_channels = await db.get_force_sub_channels()
    auto_delete_time = await db.get_setting("auto_delete_time") or AUTO_DELETE_TIME
    
    text = (
        "⚙️ **Admin Panel**\n\n"
        f"📊 **Current Settings:**\n\n"
        f"🔔 Force Subscribe Channels: {len(force_channels)}\n"
        f"⏰ Auto-Delete Time: {get_readable_time(auto_delete_time)}\n\n"
        "Select an option below:"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Manage Force-Sub Channels", callback_data="manage_fsub")],
        [InlineKeyboardButton("⏰ Change Auto-Delete Time", callback_data="change_delete_time")],
        [InlineKeyboardButton("📝 Update Messages", callback_data="update_messages")],
        [InlineKeyboardButton("📊 View Stats", callback_data="view_stats")],
        [InlineKeyboardButton("❌ Close", callback_data="close_panel")]
    ])
    
    await message.reply_text(text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^manage_fsub$") & filters.create(lambda _, __, q: q.from_user.id in ADMINS))
async def manage_force_sub(client: Client, callback: CallbackQuery):
    """Manage force subscribe channels"""
    await callback.answer()
    
    force_channels = await db.get_force_sub_channels()
    
    text = "📢 **Manage Force Subscribe Channels**\n\n"
    
    if force_channels:
        text += "**Current Channels:**\n"
        for idx, channel_id in enumerate(force_channels, 1):
            try:
                chat = await client.get_chat(channel_id)
                text += f"{idx}. {chat.title} (`{channel_id}`)\n"
            except:
                text += f"{idx}. Channel ID: `{channel_id}`\n"
    else:
        text += "No force subscribe channels set.\n"
    
    text += "\n**Commands:**\n"
    text += "• `/addfsub <channel_id>` - Add channel\n"
    text += "• `/delfsub <channel_id>` - Remove channel\n"
    text += "• `/listfsub` - List all channels"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="back_to_settings")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@Client.on_message(filters.command('addfsub') & filters.private & is_admin_filter())
async def add_force_sub_channel(client: Client, message: Message):
    """Add a force subscribe channel"""
    
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/addfsub <channel_id>`\n\n"
            "Example: `/addfsub -1001234567890`"
        )
        return
    
    try:
        channel_id = int(message.command[1])
        
        # Verify bot is admin in the channel
        try:
            chat = await client.get_chat(channel_id)
            member = await client.get_chat_member(channel_id, client.me.id)
            
            if member.status not in ["administrator", "creator"]:
                await message.reply_text(
                    f"❌ I'm not an admin in **{chat.title}**!\n"
                    "Please make me admin first."
                )
                return
        except Exception as e:
            await message.reply_text(f"❌ Error accessing channel: {str(e)}")
            return
        
        # Add to database
        success = await db.add_force_sub_channel(channel_id)
        
        if success:
            await message.reply_text(
                f"✅ Added **{chat.title}** to force subscribe!\n"
                f"Channel ID: `{channel_id}`"
            )
            LOGGER(__name__).info(f"Admin {message.from_user.id} added force-sub channel: {channel_id}")
        else:
            await message.reply_text("⚠️ This channel is already in the list!")
    
    except ValueError:
        await message.reply_text("❌ Invalid channel ID! Must be a number.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER(__name__).error(f"Error adding force-sub channel: {e}")

@Client.on_message(filters.command('delfsub') & filters.private & is_admin_filter())
async def delete_force_sub_channel(client: Client, message: Message):
    """Remove a force subscribe channel"""
    
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/delfsub <channel_id>`\n\n"
            "Example: `/delfsub -1001234567890`"
        )
        return
    
    try:
        channel_id = int(message.command[1])
        
        success = await db.remove_force_sub_channel(channel_id)
        
        if success:
            await message.reply_text(f"✅ Removed channel `{channel_id}` from force subscribe!")
            LOGGER(__name__).info(f"Admin {message.from_user.id} removed force-sub channel: {channel_id}")
        else:
            await message.reply_text("⚠️ This channel is not in the list!")
    
    except ValueError:
        await message.reply_text("❌ Invalid channel ID! Must be a number.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command('listfsub') & filters.private & is_admin_filter())
async def list_force_sub_channels(client: Client, message: Message):
    """List all force subscribe channels"""
    
    force_channels = await db.get_force_sub_channels()
    
    if not force_channels:
        await message.reply_text("📢 No force subscribe channels configured.")
        return
    
    text = "📢 **Force Subscribe Channels:**\n\n"
    
    for idx, channel_id in enumerate(force_channels, 1):
        try:
            chat = await client.get_chat(channel_id)
            text += f"{idx}. **{chat.title}**\n"
            text += f"   └ ID: `{channel_id}`\n"
            text += f"   └ Link: {chat.invite_link or 'N/A'}\n\n"
        except Exception as e:
            text += f"{idx}. Channel ID: `{channel_id}`\n"
            text += f"   └ Error: Unable to fetch info\n\n"
    
    await message.reply_text(text)

@Client.on_callback_query(filters.regex("^change_delete_time$") & filters.create(lambda _, __, q: q.from_user.id in ADMINS))
async def change_delete_time_callback(client: Client, callback: CallbackQuery):
    """Change auto-delete time"""
    await callback.answer()
    
    current_time = await db.get_setting("auto_delete_time") or AUTO_DELETE_TIME
    
    text = (
        "⏰ **Change Auto-Delete Time**\n\n"
        f"Current: {get_readable_time(current_time)}\n\n"
        "**Command:**\n"
        "`/setdeletetime <seconds>`\n\n"
        "**Examples:**\n"
        "• `/setdeletetime 3600` (1 hour)\n"
        "• `/setdeletetime 7200` (2 hours)\n"
        "• `/setdeletetime 25200` (7 hours)\n"
        "• `/setdeletetime 0` (disable auto-delete)"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="back_to_settings")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@Client.on_message(filters.command('setdeletetime') & filters.private & is_admin_filter())
async def set_delete_time(client: Client, message: Message):
    """Set auto-delete time"""
    
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/setdeletetime <seconds>`\n\n"
            "Example: `/setdeletetime 7200` (2 hours)"
        )
        return
    
    try:
        seconds = int(message.command[1])
        
        if seconds < 0:
            await message.reply_text("❌ Time must be 0 or positive!")
            return
        
        # Save to database
        await db.set_setting("auto_delete_time", seconds)
        
        if seconds == 0:
            await message.reply_text("✅ Auto-delete disabled!")
        else:
            await message.reply_text(
                f"✅ Auto-delete time set to **{get_readable_time(seconds)}**!\n\n"
                "⚠️ This only affects SHORT category files.\n"
                "Movie files remain permanent."
            )
        
        LOGGER(__name__).info(f"Admin {message.from_user.id} changed auto-delete time to {seconds}s")
    
    except ValueError:
        await message.reply_text("❌ Invalid time! Must be a number in seconds.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_callback_query(filters.regex("^view_stats$") & filters.create(lambda _, __, q: q.from_user.id in ADMINS))
async def view_stats_callback(client: Client, callback: CallbackQuery):
    """View bot statistics"""
    await callback.answer("Loading stats...")
    
    total_users = await db.total_users_count()
    total_files = await db.total_files_count()
    force_channels = await db.get_force_sub_channels()
    
    text = (
        "📊 **Bot Statistics**\n\n"
        f"👥 Total Users: {total_users}\n"
        f"📦 Total Files: {total_files}\n"
        f"📢 Force-Sub Channels: {len(force_channels)}\n"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="back_to_settings")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^back_to_settings$") & filters.create(lambda _, __, q: q.from_user.id in ADMINS))
async def back_to_settings(client: Client, callback: CallbackQuery):
    """Go back to main settings menu"""
    await callback.answer()
    
    force_channels = await db.get_force_sub_channels()
    auto_delete_time = await db.get_setting("auto_delete_time") or AUTO_DELETE_TIME
    
    text = (
        "⚙️ **Admin Panel**\n\n"
        f"📊 **Current Settings:**\n\n"
        f"🔔 Force Subscribe Channels: {len(force_channels)}\n"
        f"⏰ Auto-Delete Time: {get_readable_time(auto_delete_time)}\n\n"
        "Select an option below:"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Manage Force-Sub Channels", callback_data="manage_fsub")],
        [InlineKeyboardButton("⏰ Change Auto-Delete Time", callback_data="change_delete_time")],
        [InlineKeyboardButton("📝 Update Messages", callback_data="update_messages")],
        [InlineKeyboardButton("📊 View Stats", callback_data="view_stats")],
        [InlineKeyboardButton("❌ Close", callback_data="close_panel")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^close_panel$"))
async def close_panel(client: Client, callback: CallbackQuery):
    """Close admin panel"""
    await callback.answer()
    await callback.message.delete()