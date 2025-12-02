# ⚡ Quick Start Guide (5 Minutes)

## 🎯 Goal
Get your test bot running to verify old links still work!

---

## ✅ Step 1: Create Test Bot (2 min)

1. Open [@BotFather](https://t.me/BotFather)
2. Send: `/newbot`
3. Name: `My Test Bot` (any name)
4. Username: `mytestbot123_bot` (must end with `_bot`)
5. **Copy the token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

## ✅ Step 2: Create Movie Channel (1 min)

1. Create new **Private Channel**
2. Name: `Movie Files`
3. Add your test bot as admin (all permissions)
4. Forward any message from channel to [@MissRose_bot](https://t.me/MissRose_bot)
5. Type `/id` - **Copy the channel ID** (like `-1001234567890`)

---

## ✅ Step 3: Setup Code (1 min)

Create `.env` file:

```bash
# Your existing credentials (from my.telegram.org)
API_ID=12345678
API_HASH=abc123def456

# NEW TEST BOT TOKEN
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# SAME AS PRODUCTION (IMPORTANT!)
CHANNEL_ID=-1001234567890          # Your existing SHORT channel
DATABASE_URL=mongodb+srv://...      # Your existing MongoDB URL
DATABASE_NAME=filesharexbot         # Your existing DB name

# NEW MOVIE CHANNEL
MOVIE_CHANNEL_ID=-1009876543210    # Your new movie channel

# Your user ID
OWNER_ID=123456789
ADMINS=123456789

# Auto-delete (7 hours = 25200 seconds)
AUTO_DELETE_TIME=25200

# Disable force-sub for testing
FORCE_SUB_CHANNELS=0
```

---

## ✅ Step 4: Install & Run (1 min)

```bash
pip3 install -r requirements.txt
python3 bot.py
```

**Should see:**
```
✓ Database Connected Successfully!
✓ Bot Started as @mytestbot123_bot!
✓ SHORT Database Channel: Your Channel Name
✓ MOVIE Database Channel: Movie Files
```

---

## 🧪 CRITICAL TEST: Old Links

**THIS MUST WORK OR DON'T PROCEED!**

1. Get an old link from your production bot
2. Send it to your TEST bot
3. **Does the file come?**
   - ✅ YES → Perfect! Continue to full testing
   - ❌ NO → **STOP!** Check MongoDB settings

---

## 🎬 Test Movie Feature (30 sec)

1. Forward a video to your **Movie channel**
2. Bot replies with link
3. Click the link
4. **Check:** No auto-delete warning (permanent file!)

---

## 📦 Test Short Feature (30 sec)

1. Send a video directly to test bot (DM)
2. Bot forwards to SHORT channel and gives link
3. Click the link
4. **Check:** Auto-delete warning shows!

---

## ✅ Success Checklist

- [ ] Bot started without errors
- [ ] Old links work (MOST IMPORTANT!)
- [ ] Movie channel creates permanent links
- [ ] Short channel creates auto-delete links
- [ ] Direct upload to bot goes to SHORT

**All checked? You're ready!** 🎉

---

## ⚠️ Common Issues

### "Database Connection Error"
→ Check `DATABASE_URL` is correct

### "Error connecting to channel"
→ Bot must be admin in BOTH channels

### Old links don't work
→ **CRITICAL!** Verify:
- `DATABASE_URL` exactly same as production
- `DATABASE_NAME` exactly same
- `CHANNEL_ID` exactly same

### Bot doesn't respond
→ Check bot token is correct

---

## 📚 Next Steps

Once basic test passes:

1. Read `DEPLOYMENT_GUIDE.md` for full testing
2. Test all features (admin panel, batch, etc.)
3. When everything works → Deploy to production!

---

## 🆘 Need Help?

**Check logs:**
```bash
tail -f log.txt
```

**Test MongoDB connection:**
```python
from database.database import db
import asyncio

async def test():
    users = await db.total_users_count()
    print(f"Total users: {users}")

asyncio.run(test())
```

---

## 🎉 Ready for Full Testing?

See `DEPLOYMENT_GUIDE.md` for complete testing checklist!