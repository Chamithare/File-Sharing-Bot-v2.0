from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from database.database import db
from config import LOGGER
from helper_func import is_admin_filter
import asyncio

@Client.on_message(filters.command('broadcast') & filters.private & is_admin_filter())
async def broadcast_command(client: Client, message: Message):
    """
    Broadcast message to all users
    Usage: /broadcast (reply to a message)
    """
    
    # Check if replying to a message
    if not message.reply_to_message:
        await message.reply_text(
            "📢 **Broadcast Message**\n\n"
            "Reply to a message with `/broadcast` to send it to all users.\n\n"
            "**Supported:**\n"
            "• Text messages\n"
            "• Photos\n"
            "• Videos\n"
            "• Documents\n"
            "• Any media with caption"
        )
        return
    
    # Confirm broadcast
    total_users = await db.total_users_count()
    
    confirm_msg = await message.reply_text(
        f"📢 **Confirm Broadcast**\n\n"
        f"👥 Total users: {total_users}\n\n"
        "⏳ Starting broadcast in 5 seconds...\n"
        "Send `/cancel` to stop."
    )
    
    await asyncio.sleep(5)
    
    # Start broadcasting
    broadcast_msg = message.reply_to_message
    
    status_msg = await confirm_msg.edit_text(
        "📢 **Broadcasting...**\n\n"
        "⏳ Please wait..."
    )
    
    success = 0
    failed = 0
    deleted = 0
    blocked = 0
    
    async for user in db.get_all_users():
        user_id = user['_id']
        
        try:
            # Copy the message to user
            await broadcast_msg.copy(chat_id=user_id)
            success += 1
            
            # Update status every 50 users
            if (success + failed) % 50 == 0:
                await status_msg.edit_text(
                    f"📢 **Broadcasting...**\n\n"
                    f"✅ Success: {success}\n"
                    f"❌ Failed: {failed}\n"
                    f"🚫 Blocked: {blocked}\n"
                    f"❌ Deleted: {deleted}\n\n"
                    f"⏳ Progress: {success + failed}/{total_users}"
                )
            
            await asyncio.sleep(0.1)  # Avoid flood
        
        except FloodWait as e:
            LOGGER(__name__).warning(f"FloodWait: {e.value}s")
            await asyncio.sleep(e.value)
            
            # Retry
            try:
                await broadcast_msg.copy(chat_id=user_id)
                success += 1
            except:
                failed += 1
        
        except InputUserDeactivated:
            deleted += 1
            await db.delete_user(user_id)
        
        except UserIsBlocked:
            blocked += 1
        
        except Exception as e:
            failed += 1
            LOGGER(__name__).error(f"Broadcast error for {user_id}: {e}")
    
    # Final status
    await status_msg.edit_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"📊 **Statistics:**\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"🚫 Blocked: {blocked}\n"
        f"🗑 Deleted Accounts: {deleted}\n\n"
        f"👥 Total: {total_users}\n"
        f"📈 Success Rate: {(success/total_users)*100:.1f}%"
    )
    
    LOGGER(__name__).info(
        f"Broadcast completed by admin {message.from_user.id}: "
        f"{success} success, {failed} failed"
    )

@Client.on_message(filters.command('forward_broadcast') & filters.private & is_admin_filter())
async def forward_broadcast_command(client: Client, message: Message):
    """
    Forward a message from a channel to all users
    Usage: /forward_broadcast (reply to a forwarded message)
    """
    
    if not message.reply_to_message:
        await message.reply_text(
            "📢 **Forward Broadcast**\n\n"
            "Reply to a forwarded message with `/forward_broadcast`"
        )
        return
    
    if not message.reply_to_message.forward_from_chat:
        await message.reply_text(
            "❌ The replied message must be a forwarded message from a channel!"
        )
        return
    
    # Get total users
    total_users = await db.total_users_count()
    
    status_msg = await message.reply_text(
        f"📢 **Starting Forward Broadcast...**\n\n"
        f"👥 Total users: {total_users}\n"
        "⏳ Please wait..."
    )
    
    success = 0
    failed = 0
    deleted = 0
    blocked = 0
    
    forward_msg = message.reply_to_message
    
    async for user in db.get_all_users():
        user_id = user['_id']
        
        try:
            # Forward the message
            await forward_msg.forward(chat_id=user_id)
            success += 1
            
            # Update status every 50 users
            if (success + failed) % 50 == 0:
                await status_msg.edit_text(
                    f"📢 **Forward Broadcasting...**\n\n"
                    f"✅ Success: {success}\n"
                    f"❌ Failed: {failed}\n"
                    f"🚫 Blocked: {blocked}\n"
                    f"❌ Deleted: {deleted}\n\n"
                    f"⏳ Progress: {success + failed}/{total_users}"
                )
            
            await asyncio.sleep(0.1)
        
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await forward_msg.forward(chat_id=user_id)
                success += 1
            except:
                failed += 1
        
        except InputUserDeactivated:
            deleted += 1
            await db.delete_user(user_id)
        
        except UserIsBlocked:
            blocked += 1
        
        except Exception as e:
            failed += 1
    
    # Final status
    await status_msg.edit_text(
        f"✅ **Forward Broadcast Complete!**\n\n"
        f"📊 **Statistics:**\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"🚫 Blocked: {blocked}\n"
        f"🗑 Deleted Accounts: {deleted}\n\n"
        f"👥 Total: {total_users}\n"
        f"📈 Success Rate: {(success/total_users)*100:.1f}%"
    )
    
    LOGGER(__name__).info(f"Forward broadcast by admin {message.from_user.id}: {success} success")