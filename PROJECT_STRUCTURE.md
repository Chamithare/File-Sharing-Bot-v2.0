# 📁 Project Structure & File Guide

## 🗂️ Directory Structure

```
File-Sharing-Bot-v2/
│
├── bot.py                          # Main bot file - START HERE
├── config.py                       # Configuration & environment variables
├── helper_func.py                  # Helper functions (force-sub, encoding, etc.)
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── DEPLOYMENT_GUIDE.md            # Deployment instructions
├── PROJECT_STRUCTURE.md           # This file
├── log.txt                        # Bot logs (auto-generated)
│
├── database/
│   ├── __init__.py                # Empty file (required for Python package)
│   └── database.py                # MongoDB operations & queries
│
└── plugins/                       # Bot command handlers
    ├── __init__.py                # Empty file (required)
    ├── start.py                   # /start command & file delivery
    ├── channel_post.py            # Handle posts in database channels
    ├── admin_panel.py             # Admin panel & settings
    ├── batch.py                   # /batch and /genlink commands
    └── broadcast.py               # /broadcast command
```

---

## 📄 File Descriptions

### Core Files

#### `bot.py` - Main Bot File
- **Purpose:** Entry point, initializes the bot
- **Key Features:**
  - Connects to Telegram
  - Verifies database channels
  - Starts plugin system
- **Don't modify unless:** Changing bot initialization

#### `config.py` - Configuration
- **Purpose:** Loads all environment variables
- **Key Features:**
  - API credentials
  - Database channel IDs (SHORT & MOVIE)
  - Auto-delete settings
  - Force-sub channels
  - Custom messages
- **Modify when:** Changing default messages or adding new config options

#### `helper_func.py` - Helper Functions
- **Purpose:** Reusable utility functions
- **Key Functions:**
  - `is_subscribed()` - Check force-sub status
  - `handle_force_sub()` - Handle force-sub flow
  - `encode()/decode()` - Base64 link encoding
  - `get_readable_time()` - Format seconds to readable time
- **Modify when:** Adding new utility functions

---

### Database Files

#### `database/database.py` - Database Operations
- **Purpose:** All MongoDB interactions
- **Key Methods:**
  - User management (`add_user`, `get_all_users`)
  - File management (`add_file`, `get_file`) ← **IMPORTANT!**
  - Settings management (`get_setting`, `set_setting`)
  - Force-sub management (`add_force_sub_channel`)
- **Critical:** The `category` field in `add_file()` determines auto-delete behavior

---

### Plugin Files (Command Handlers)

#### `plugins/start.py` - Start Command
- **Purpose:** Handle /start command and file delivery
- **Key Functions:**
  - `start_command()` - Welcome message
  - `handle_file_request()` - Deliver single file
  - `handle_batch_request()` - Deliver batch files
  - `delete_file_after_time()` - Auto-delete scheduler
- **Critical Features:**
  - Checks force-sub before delivery
  - Determines category (SHORT/MOVIE) from database
  - Schedules auto-delete only for SHORT category
  - Adds auto-delete warning to captions

#### `plugins/channel_post.py` - Channel Handlers
- **Purpose:** Monitor database channels for new posts
- **Key Functions:**
  - `handle_short_channel_post()` - SHORT channel (auto-delete)
  - `handle_movie_channel_post()` - MOVIE channel (permanent)
  - `handle_direct_upload()` - Files sent to bot DM
- **Critical Features:**
  - Saves files with correct category
  - Generates shareable links
  - Shows category info (auto-delete vs permanent)

#### `plugins/admin_panel.py` - Admin Panel
- **Purpose:** In-bot admin settings management
- **Key Commands:**
  - `/settings` - Main admin panel
  - `/addfsub` - Add force-sub channel
  - `/delfsub` - Remove force-sub channel
  - `/listfsub` - List force-sub channels
  - `/setdeletetime` - Change auto-delete time
- **Features:**
  - Interactive button-based UI
  - Live stats display
  - No need to touch server!

#### `plugins/batch.py` - Batch & GenLink
- **Purpose:** Generate links for single/multiple files
- **Key Commands:**
  - `/batch` - Create batch link (SHORT only)
  - `/genlink` - Generate single link (SHORT or MOVIE)
- **Features:**
  - Step-by-step forwarding process
  - Validates message source channel
  - Shows category info in response

#### `plugins/broadcast.py` - Broadcasting
- **Purpose:** Send messages to all users
- **Key Commands:**
  - `/broadcast` - Copy message to all users
  - `/forward_broadcast` - Forward message to all users
- **Features:**
  - Real-time progress updates
  - Handles FloodWait
  - Removes deleted/blocked users
  - Shows success statistics

---

## 🔑 Key Concepts

### Category System
Files are stored with a `category` field:
- **`"short"`** - Auto-delete enabled (from SHORT channel or bot DM)
- **`"movie"`** - Permanent (from MOVIE channel)

**Flow:**
1. File arrives in channel → `channel_post.py` detects it
2. Saved to MongoDB with category → `database.py`
3. User clicks link → `start.py` checks category
4. If "short" → Schedule auto-delete
5. If "movie" → No auto-delete

### Database Structure

**Collections:**
1. **users** - User information
   ```json
   {
     "_id": 123456789,
     "first_name": "John",
     "username": "john_doe"
   }
   ```

2. **files** - File references
   ```json
   {
     "_id": 12345,           // Message ID
     "file_ref": 12345,      // Reference ID
     "category": "short"     // or "movie"
   }
   ```

3. **settings** - Bot settings (NEW!)
   ```json
   {
     "_id": "force_sub_channels",
     "value": [-1001234567890, -1009876543210]
   }
   ```

### Force Subscribe System

**Two levels:**
1. **Config-based** - `FORCE_SUB_CHANNELS` in `.env`
2. **Database-based** - Added via `/addfsub` (dynamic)

Both are merged and checked together!

---

## 🛠️ Common Modifications

### Add New Command
1. Create new file in `plugins/` folder
2. Use decorator: `@Client.on_message(filters.command('yourcommand'))`
3. Import necessary modules

Example:
```python
from pyrogram import Client, filters
from helper_func import is_admin_filter

@Client.on_message(filters.command('hello') & is_admin_filter())
async def hello_command(client, message):
    await message.reply_text("Hello, Admin!")
```

### Change Auto-Delete Behavior
Modify `plugins/start.py`:
- `handle_file_request()` - Where auto-delete is scheduled
- `delete_file_after_time()` - The deletion function

### Add New Database Field
1. Modify `database/database.py`
2. Add new method for the field
3. Use in plugins

---

## 🚨 Critical Files - Don't Break These!

### HIGH RISK (Modify carefully)
- `database/database.py` - Data loss risk
- `plugins/start.py` - Breaks file delivery
- `config.py` - Bot won't start if broken

### MEDIUM RISK
- `plugins/channel_post.py` - Links won't generate
- `helper_func.py` - Multiple features break

### LOW RISK (Safe to modify)
- `plugins/admin_panel.py` - Only affects admin UI
- `plugins/broadcast.py` - Only affects broadcasting
- `plugins/batch.py` - Only affects batch creation

---

## 🔍 Debugging Guide

### Bot Won't Start
Check:
1. `config.py` - All env variables set?
2. `bot.py` - MongoDB connection working?
3. Bot is admin in BOTH channels?

### Files Not Delivering
Check:
1. `plugins/start.py` logs
2. Database has the file ID?
3. Correct channel ID in config?

### Auto-Delete Not Working
Check:
1. File category is "short"?
2. `AUTO_DELETE_TIME` is set (not 0)?
3. Bot hasn't restarted? (tasks lost on restart)

### Links Not Generating
Check:
1. `plugins/channel_post.py` running?
2. Bot sees new channel posts?
3. Bot is admin in channel?

---

## 📚 Learning Resources

### Understanding Pyrogram
- [Pyrogram Docs](https://docs.pyrogram.org/)
- Handlers: `@Client.on_message()`
- Filters: `filters.command()`, `filters.private`, etc.

### Understanding MongoDB
- [Motor Docs](https://motor.readthedocs.io/)
- Async operations: `await db.collection.find_one()`

### Understanding Asyncio
- `async def` - Async function
- `await` - Wait for async operation
- `asyncio.create_task()` - Run in background

---

## 🎯 Summary

**To understand the bot:**
1. Start with `bot.py` - Entry point
2. Read `config.py` - Configuration
3. Study `plugins/start.py` - Main file delivery logic
4. Check `plugins/channel_post.py` - Link generation
5. Explore `database/database.py` - Data storage

**Critical concept:** The `category` field determines if a file auto-deletes!

**Need to modify?** Most changes will be in `plugins/` folder.