# 🚀 File Sharing Bot - Deployment Guide

## 📋 Pre-Deployment Checklist

### 1️⃣ Create Test Bot
1. Go to [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose name: `YourBot Test` (or any name)
4. Choose username: `yourbottest_bot`
5. **Save the bot token!**

### 2️⃣ Create Movie Database Channel
1. Create a new **private channel**
2. Name it: `Movie Files Database` (or any name)
3. Add your test bot as **admin** with all permissions
4. Get channel ID:
   - Forward any message from channel to [@MissRose_bot](https://t.me/MissRose_bot)
   - Send `/id` to get channel ID (will be like `-1001234567890`)
5. **Save the channel ID!**

### 3️⃣ Get Existing Database Info
You already have:
- ✅ MongoDB connection string
- ✅ SHORT database channel ID
- ✅ SHORT database channel (bot already admin)

---

## 🔧 Setup Steps

### Step 1: Clone/Download the Code
```bash
git clone YOUR_NEW_REPO_URL
cd File-Sharing-Bot-Test
```

### Step 2: Install Dependencies
```bash
pip3 install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file or set environment variables:

```bash
# CRITICAL - Test Bot Configuration
API_ID=YOUR_API_ID
API_HASH=YOUR_API_HASH
BOT_TOKEN=YOUR_TEST_BOT_TOKEN  # NEW test bot token

# Database Channels
CHANNEL_ID=-1001234567890  # YOUR EXISTING SHORT CHANNEL (SAME AS PRODUCTION)
MOVIE_CHANNEL_ID=-1009876543210  # YOUR NEW MOVIE CHANNEL

# Admin
OWNER_ID=YOUR_USER_ID
ADMINS=YOUR_USER_ID

# MongoDB (SAME AS PRODUCTION - IMPORTANT!)
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=filesharexbot  # SAME AS PRODUCTION

# Auto-delete (7 hours)
AUTO_DELETE_TIME=25200

# Optional: Force Subscribe (leave as 0 for testing)
FORCE_SUB_CHANNELS=0
```

### Step 4: Verify Bot Permissions

**SHORT Channel:**
- ✅ Bot already admin (from production)
- ✅ Has all permissions

**MOVIE Channel:**
- ✅ Make bot admin
- ✅ Give these permissions:
  - Post messages
  - Edit messages
  - Delete messages
  - Manage chat

### Step 5: Start the Bot
```bash
python3 bot.py
```

You should see:
```
INFO - Bot Started as @yourbottest_bot!
INFO - SHORT Database Channel: Your Short Channel (-1001234567890)
INFO - MOVIE Database Channel: Movie Files Database (-1009876543210)
```

---

## 🧪 Testing Checklist

### Test 1: Old Links Work ✅
**Goal:** Verify existing 13,000+ user links still work

1. Get an old link from your production bot
2. Send it to your test bot
3. **Expected:** File should be delivered
4. **Expected:** Auto-delete should work (if still in 7hr window)

**If this fails, STOP and debug!**

---

### Test 2: SHORT Channel (Auto-Delete) ✅

**A. Send file to SHORT channel:**
1. Forward any video to SHORT database channel
2. Bot should reply with link
3. **Expected:** Message says "Auto-Delete"

**B. Click the link:**
1. Click the generated link
2. **Expected:** File received
3. **Expected:** Warning message shows delete time
4. **Expected:** File deletes after set time

---

### Test 3: MOVIE Channel (Permanent) ✅

**A. Send file to MOVIE channel:**
1. Forward a movie to MOVIE database channel
2. Bot should reply with link
3. **Expected:** Message says "Permanent"

**B. Click the link:**
1. Click the generated link
2. **Expected:** File received
3. **Expected:** NO auto-delete warning
4. **Expected:** File stays forever

---

### Test 4: Direct Upload to Bot ✅

**Goal:** Files sent directly go to SHORT

1. Send a video directly to test bot (DM)
2. **Expected:** Bot forwards to SHORT channel
3. **Expected:** Bot replies with SHORT category link
4. **Expected:** Auto-delete enabled

---

### Test 5: Multiple Force-Sub Channels ✅

**A. Add force-sub channels:**
```
/settings
→ Manage Force-Sub Channels
→ /addfsub -1001234567890
```

**B. Test force-sub:**
1. Try to access a file without joining
2. **Expected:** Bot asks to join channel(s)
3. Join the channel
4. Try again
5. **Expected:** File delivered

**C. Test multiple channels:**
```
/addfsub -1009876543210
```
1. Try to access file
2. **Expected:** Must join BOTH channels

---

### Test 6: Admin Panel ✅

**A. Access admin panel:**
```
/settings
```
**Expected:** Admin panel opens with buttons

**B. Change auto-delete time:**
```
/setdeletetime 3600
```
**Expected:** Time changed to 1 hour

**C. List force-sub channels:**
```
/listfsub
```
**Expected:** Shows all configured channels

---

### Test 7: Batch Links ✅

**A. Create batch:**
```
/batch
```
1. Forward first message from SHORT channel
2. Forward last message from SHORT channel
3. **Expected:** Batch link created

**B. Test batch link:**
1. Click batch link
2. **Expected:** All files received
3. **Expected:** All files auto-delete

---

### Test 8: Broadcast ✅

**A. Test broadcast:**
```
/broadcast (reply to any message)
```
**Expected:** Message sent to all users

**B. Check stats:**
```
/settings → View Stats
```
**Expected:** Shows total users, files

---

## ⚠️ Critical Verification Points

### ✅ MUST PASS:
1. **Old links work** - If this fails, DO NOT deploy to production!
2. **SHORT auto-delete works** - Files must delete after time
3. **MOVIE files permanent** - Must NOT delete automatically
4. **Database shared** - Both bots see same users/files
5. **No data loss** - MongoDB data intact

### 🔄 Migration Path if All Tests Pass:

**Option A: Switch Tokens (Recommended)**
1. Stop production bot
2. Change production bot's config to use new code
3. Deploy new code with production token
4. Old links keep working ✅

**Option B: Keep Test Bot**
1. Announce new bot to users
2. Gradually migrate users
3. Keep old bot running for old links

---

## 🐛 Troubleshooting

### Issue: "Database Connection Error"
**Solution:** Check MongoDB URL is correct

### Issue: "Error connecting to channel"
**Solution:** 
- Verify channel IDs are correct (include the `-100` prefix)
- Make bot admin in BOTH channels
- Check bot has all permissions

### Issue: "Old links don't work"
**Solution:**
- Verify `DATABASE_URL` is EXACTLY same as production
- Verify `DATABASE_NAME` is same
- Verify `CHANNEL_ID` (SHORT) is same

### Issue: "Files not auto-deleting"
**Solution:**
- Check `AUTO_DELETE_TIME` is set (not 0)
- Verify file is from SHORT category
- Check bot logs for errors

---

## 📊 Monitoring After Deployment

Monitor these for 24 hours:

1. **Error logs** - Check `log.txt`
2. **User complaints** - Old links working?
3. **Auto-delete** - Files deleting properly?
4. **Movie links** - Staying permanent?
5. **Database size** - Growing normally?

---

## 🎉 Success Criteria

✅ All old links work
✅ SHORT files auto-delete
✅ MOVIE files stay permanent
✅ Admin panel works
✅ Force-sub works
✅ Batch works
✅ Broadcast works
✅ No data loss

**If all above pass → Ready for production! 🚀**

---

## 📞 Need Help?

If any test fails:
1. Check logs in `log.txt`
2. Verify all environment variables
3. Verify bot permissions in channels
4. Test with fresh MongoDB to isolate issue

**NEVER deploy to production if old links test fails!**