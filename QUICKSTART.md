# Quick Start Guide - MeowDow Bot

## ✅ What You Have
- Discord token is configured ✓
- Bot prefix is set to `.` ✓
- All dependencies installed ✓

## ⚠️ What Needs Fixing

### 1. OWNER_ID (Optional but Recommended)
**Current:** `i.m.diablo` (username - won't work)
**Needs:** Your Discord User ID (numbers)

**How to get it:**
1. Open Discord
2. Settings → Advanced → Enable "Developer Mode"
3. Right-click your username → "Copy User ID"
4. Update `.env` file:
   ```
   OWNER_ID=123456789012345678
   ```

### 2. Optional API Keys (Can Skip for Now)

**Giphy** (for `/gif` command):
- Get free key at: https://developers.giphy.com/
- Update: `GIPHY_API_KEY=your_actual_key`

**Spotify** (for Spotify music links):
- Get free credentials at: https://developer.spotify.com/dashboard
- Update both `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`

## 🚀 Running the Bot

### Current Status
The bot should run with just the Discord token! The OWNER_ID warning is just informational.

### Start the Bot
```bash
python bot.py
```

### Expected Output
```
Warning: OWNER_ID must be a numeric Discord user ID...
INFO - Setting up bot...
INFO - Database connected
INFO - Loaded cog: utility
INFO - Synced X slash commands
INFO - Bot is ready! Logged in as YourBotName
```

### Test Commands
Once the bot is online in Discord:
- `.ping` - Check if bot responds
- `/ping` - Test slash command
- `.calc 5 + 3` - Test calculator
- `.roll` - Roll a dice
- `.8ball Will this work?` - Magic 8-ball

## ⚠️ Known Limitations (Until Migration Complete)

The new modular bot currently only has:
- ✅ Utility commands (ping, calc, roll, coinflip, 8ball)
- ❌ Music commands (need to migrate from old main.py)
- ❌ Moderation commands (need to migrate)
- ❌ Fun commands (need to migrate)
- ❌ Economy/Leveling (need to implement)

## 🔧 Next Steps

1. **Test the bot** - Make sure it starts and basic commands work
2. **Get your User ID** - Update OWNER_ID in `.env`
3. **Migrate commands** - Follow the walkthrough to move commands from old main.py to cogs
4. **Add API keys** - If you want GIF and Spotify features

## 🆘 Troubleshooting

### Bot won't start
- Check if Discord token is correct
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Commands don't work
- Make sure bot has proper permissions in Discord server
- Check if Message Content Intent is enabled in Discord Developer Portal

### Music doesn't work
- Music commands haven't been migrated yet
- Need to create `cogs/music.py` (see walkthrough)

## 📚 Documentation

- **Full README**: `README.md`
- **Deployment Guide**: `DEPLOYMENT.md`
- **Migration Walkthrough**: See artifacts in chat
- **Implementation Plan**: See artifacts in chat

---

**You're ready to test the bot! 🎉**

Run `python bot.py` and check if it comes online in Discord!
