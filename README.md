# 🤖 File Sharing Bot v2.0 - Enhanced Edition

> **Telegram bot for file sharing with dual category system: Auto-delete for short content, permanent for movies**

[![Pyrogram](https://img.shields.io/badge/Pyrogram-v2.0-blue)](https://docs.pyrogram.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Compatible-green)](https://www.mongodb.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)](https://www.python.org/)

---

## 🌟 What's New in v2.0

### Major Features
✅ **Dual Category System**
- SHORT category: Auto-delete after configurable time (default 7 hours)
- MOVIE category: Permanent storage (no auto-delete)

✅ **Multiple Force Subscribe**
- Add unlimited force-subscribe channels
- Manage dynamically via bot commands

✅ **In-Bot Admin Panel**
- Change settings without touching server
- Interactive button-based interface
- Real-time statistics

✅ **Backward Compatible**
- All existing links keep working
- Uses same MongoDB database
- Zero data migration needed

---

## 📋 Features Overview

### For Users
- 📥 Download files via shareable links
- 🔒 Force-subscribe to channels (configurable)
- ⏰ Auto-delete warnings for temporary files
- 💾 Permanent movie files

### For Admins
- 🎬 Two database channels (SHORT + MOVIE)
- ⚙️ In-bot settings panel
- 📊 Real-time statistics
- 📢 Broadcast to all users
- 📦 Batch link generation
- 🔗 Single link generation
- 🛡️ Content protection

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB database
- Telegram Bot Token
- Two Telegram channels (SHORT + MOVIE)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd File-Sharing-Bot-v2

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run bot
python3 bot.py
```

**See [QUICK_START.md](QUICK_START.md) for detailed 5-minute setup guide!**

---

## 📂 Project Structure

```
├── bot.py                    # Main bot file
├── config.py                 # Configuration
├── helper_func.py            # Utility functions
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
│
├── database/
│   └── database.py          # MongoDB operations
│
└── plugins/
    ├── start.py             # File delivery
    ├── channel_post.py      # Channel monitoring
    ├── admin_panel.py       # Admin commands
    ├── batch.py             # Batch/GenLink
    └── broadcast.py         # Broadcasting
```

**See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed code guide!**

---

## ⚙️ Configuration

### Required Variables

```bash
# Telegram API (from my.telegram.org)
API_ID=12345678
API_HASH=your_api_hash

# Bot Token (from @BotFather)
BOT_TOKEN=your_bot_token

# Database Channels
CHANNEL_ID=-1001234567890        # SHORT channel (auto-delete)
MOVIE_CHANNEL_ID=-1009876543210  # MOVIE channel (permanent)

# MongoDB
DATABASE_URL=mongodb+srv://...
DATABASE_NAME=filesharexbot

# Admin
OWNER_ID=123456789
ADMINS=123456789 987654321
```

**See [.env.example](.env.example) for all configuration options!**

---

## 📖 User Guide

### For Bot Users

**Getting Files:**
1. Click on shared link
2. Join required channels (if any)
3. Receive file
4. Note auto-delete warning (if SHORT category)

### For Admins

**Creating Links:**

**Method 1: Send to Channels**
- Send to SHORT channel → Auto-delete link
- Send to MOVIE channel → Permanent link

**Method 2: Send to Bot DM**
- Send directly to bot → Forwards to SHORT (auto-delete)

**Method 3: Use Commands**
```bash
/genlink          # Generate link from forwarded message
/batch            # Create batch link for multiple files
```

**Managing Settings:**
```bash
/settings         # Open admin panel
/addfsub <id>     # Add force-subscribe channel
/delfsub <id>     # Remove force-subscribe channel
/listfsub         # List all force-subscribe channels
/setdeletetime <sec>  # Change auto-delete time
```

**Broadcasting:**
```bash
/broadcast        # Reply to message to broadcast
```

---

## 🧪 Testing Guide

### Critical Test: Old Links

**MUST PASS before production deployment!**

1. Create test bot with new token
2. Use SAME MongoDB database
3. Test old production links
4. Verify files are delivered

**See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete testing checklist!**

---

## 🔄 Migration from v1.0

### Safe Migration Steps

1. ✅ Keep production bot running
2. ✅ Deploy test bot with new code
3. ✅ Use SAME MongoDB database
4. ✅ Test all features thoroughly
5. ✅ Verify old links work
6. ✅ Switch to new code

**Zero downtime. Zero data loss.**

---

## 📊 How It Works

### Category System

```
┌─────────────────────┐
│   Admin sends file  │
└──────────┬──────────┘
           │
           ├─→ To SHORT channel
           │      ↓
           │   Saves as "short"
           │      ↓
           │   Auto-delete ✅
           │
           └─→ To MOVIE channel
                  ↓
               Saves as "movie"
                  ↓
               Permanent ✅
```

### File Delivery Flow

```
User clicks link
      ↓
Check force-subscribe
      ↓
Get file from database
      ↓
Check category
      ↓
   ┌──┴──┐
   │     │
SHORT  MOVIE
   │     │
   ↓     ↓
Send   Send
+ warn  file
   │
   ↓
Schedule
auto-delete
```

---

## 🛠️ Advanced Configuration

### Custom Messages

All messages are customizable via environment variables:

- `START_MESSAGE` - Welcome message
- `FORCE_SUB_MESSAGE` - Force subscribe message
- `AUTO_DELETE_MSG` - Auto-delete warning
- `CUSTOM_CAPTION` - File caption template

**Supports HTML and variables:** `{first}`, `{mention}`, `{filename}`, etc.

### Auto-Delete Time

Change globally via environment:
```bash
AUTO_DELETE_TIME=3600  # 1 hour
```

Or dynamically via bot:
```bash
/setdeletetime 7200  # 2 hours
```

### Content Protection

Prevent forwarding:
```bash
PROTECT_CONTENT=True
```

---

## 📚 Documentation

- 📖 [Quick Start Guide](QUICK_START.md) - 5-minute setup
- 🚀 [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete testing & deployment
- 📁 [Project Structure](PROJECT_STRUCTURE.md) - Code organization & modification guide
- 💾 [Environment Variables](.env.example) - All configuration options

---

## 🐛 Troubleshooting

### Bot Won't Start

**Check:**
- All environment variables set?
- MongoDB connection working?
- Bot is admin in both channels?

### Old Links Don't Work

**Verify:**
- `DATABASE_URL` exactly matches production
- `DATABASE_NAME` exactly matches production
- `CHANNEL_ID` (SHORT) exactly matches production

### Files Not Auto-Deleting

**Check:**
- File is "short" category?
- `AUTO_DELETE_TIME` > 0?
- Bot hasn't restarted (tasks lost)?

**See logs:**
```bash
tail -f log.txt
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Multiple language support
- [ ] Payment integration
- [ ] URL shortener integration
- [ ] Enhanced statistics
- [ ] Web dashboard

---

## 📜 License

This project is licensed under GNU General Public License v3.0

---

## ⚠️ Important Notes

### Before Production Deployment

✅ Test with same MongoDB database
✅ Verify all old links work
✅ Test both SHORT and MOVIE categories
✅ Test admin panel commands
✅ Run for 24 hours in test mode

### Data Safety

- ✅ MongoDB stores only metadata (IDs, references)
- ✅ Actual files stored in Telegram channels
- ✅ Backward compatible with existing data
- ✅ No data migration needed

### Performance

- Handles 13,000+ users (proven)
- Async operations for efficiency
- FloodWait handling
- Auto-cleanup of deleted users

---

## 📞 Support

Having issues?

1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Check [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. Review `log.txt` for errors
4. Verify all environment variables
5. Test with fresh MongoDB to isolate issues

---

## 🎉 Credits

- Original bot: [CodeXBotz/File-Sharing-Bot](https://github.com/CodeXBotz/File-Sharing-Bot)
- Framework: [Pyrogram](https://docs.pyrogram.org/)
- Enhanced by: Your team

---

## 📌 Version History

### v2.0 (Current)
- ✅ Dual category system (SHORT/MOVIE)
- ✅ Multiple force-subscribe
- ✅ In-bot admin panel
- ✅ Dynamic settings management
- ✅ Backward compatible

### v1.0
- Basic file sharing
- Single channel
- Single force-subscribe
- Environment-based config

---

<div align="center">

**Star ⭐ this repo if it helped you!**

Made with ❤️ for the Telegram community

</div>