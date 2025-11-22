# 🚀 Koyeb Deployment Guide - 24/7 Discord Bot Hosting

This guide will help you deploy your MeowDow Discord bot to Koyeb for **free 24/7 hosting**.

## 📋 Prerequisites

- GitHub account
- Koyeb account (free tier available)
- Discord bot token
- Your bot code pushed to a GitHub repository

## 🌟 Why Koyeb?

- ✅ **Free Tier** - Sufficient for small to medium bots
- ✅ **24/7 Uptime** - Auto-restart on crashes
- ✅ **Git Integration** - Auto-deploy on push
- ✅ **Environment Variables** - Secure configuration
- ✅ **Real-time Logs** - Easy debugging
- ✅ **No Credit Card Required** - For free tier

## 📝 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/MeowDow.git
   git push -u origin main
   ```

2. **Ensure these files are in your repository:**
   - `bot.py` (main file)
   - `requirements.txt`
   - `Dockerfile`
   - All `cogs/` and `utils/` folders
   - `.env.example` (NOT `.env` - never commit secrets!)

### Step 2: Create Koyeb Account

1. Go to [Koyeb.com](https://www.koyeb.com/)
2. Click "Sign Up"
3. Sign up with GitHub (recommended) or email
4. Verify your email if required

### Step 3: Create New App

1. Click "Create App" in Koyeb dashboard
2. Select "GitHub" as deployment method
3. Authorize Koyeb to access your GitHub
4. Select your MeowDow repository

### Step 4: Configure Deployment

#### Build Settings:
- **Builder:** Docker
- **Dockerfile:** `Dockerfile` (default)
- **Build context:** `/` (root directory)

#### Instance Settings:
- **Instance Type:** Free (Eco)
- **Regions:** Choose closest to your users
- **Scaling:** 1 instance (free tier limit)

#### Environment Variables:
Click "Add Environment Variable" and add the following:

| Name | Value | Description |
|------|-------|-------------|
| `DISCORD_TOKEN` | `your_bot_token` | Your Discord bot token (REQUIRED) |
| `OWNER_ID` | `your_user_id` | Your Discord user ID |
| `BOT_PREFIX` | `.` | Bot command prefix |
| `GIPHY_API_KEY` | `your_key` | Giphy API key (optional) |
| `SPOTIFY_CLIENT_ID` | `your_id` | Spotify client ID (optional) |
| `SPOTIFY_CLIENT_SECRET` | `your_secret` | Spotify client secret (optional) |
| `LOG_LEVEL` | `INFO` | Logging level |

**Important:** Mark `DISCORD_TOKEN` and API keys as "Secret" to hide them in logs!

### Step 5: Deploy

1. Click "Deploy"
2. Wait for build to complete (3-5 minutes)
3. Check logs for "Bot is ready!" message

### Step 6: Verify Deployment

1. Go to your Discord server
2. Check if bot is online
3. Test a command: `.ping` or `/ping`
4. Check Koyeb logs for any errors

## 🔧 Dockerfile Configuration

Your `Dockerfile` should look like this:

```dockerfile
# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Run the bot
CMD ["python", "bot.py"]
```

## 📊 Monitoring Your Bot

### View Logs:
1. Go to Koyeb dashboard
2. Click on your app
3. Go to "Logs" tab
4. View real-time logs

### Check Status:
- **Green:** Bot is running
- **Yellow:** Bot is deploying
- **Red:** Bot has crashed

### Restart Bot:
1. Go to app settings
2. Click "Redeploy"
3. Or push a new commit to GitHub (auto-deploys)

## 🔄 Auto-Deployment

Koyeb automatically redeploys when you push to GitHub:

```bash
git add .
git commit -m "Update bot"
git push
```

Wait 3-5 minutes for deployment to complete.

## 🐛 Troubleshooting

### Bot Won't Start

**Check logs for errors:**
```
Error: DISCORD_TOKEN is required
```
**Solution:** Add DISCORD_TOKEN environment variable

**Check logs for:**
```
discord.errors.LoginFailure: Improper token
```
**Solution:** Verify your Discord token is correct

### Bot Keeps Crashing

**Check logs for:**
```
ModuleNotFoundError: No module named 'discord'
```
**Solution:** Ensure `requirements.txt` is correct and committed

**Check logs for:**
```
PermissionError: [Errno 13] Permission denied: 'data/bot.db'
```
**Solution:** Ensure Dockerfile creates data directory with correct permissions

### Music Not Working

**Check logs for:**
```
FileNotFoundError: ffmpeg not found
```
**Solution:** Ensure Dockerfile installs ffmpeg (already included in example above)

### Database Issues

**Koyeb uses ephemeral storage** - database resets on restart!

**Solutions:**
1. Use external database (PostgreSQL, MongoDB)
2. Accept data loss on restarts (for testing)
3. Implement database backups

## 💾 Persistent Storage (Advanced)

For persistent data across restarts:

### Option 1: PostgreSQL (Recommended)
1. Use Koyeb's PostgreSQL addon
2. Update `utils/database.py` to use PostgreSQL
3. Install `asyncpg` in requirements.txt

### Option 2: External Database
1. Use [Railway](https://railway.app/) for PostgreSQL
2. Use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) for MongoDB
3. Add connection string to environment variables

## 📈 Scaling (Paid Plans)

Free tier limitations:
- 1 instance
- 512MB RAM
- Limited CPU

Upgrade for:
- Multiple instances
- More RAM/CPU
- Custom domains
- Priority support

## 🔒 Security Best Practices

1. **Never commit `.env` file**
   - Add to `.gitignore`
   - Use environment variables in Koyeb

2. **Mark secrets as "Secret"**
   - Hides values in logs
   - Prevents accidental exposure

3. **Rotate tokens regularly**
   - Change Discord token if compromised
   - Update in Koyeb environment variables

4. **Use least privilege**
   - Only give bot necessary permissions
   - Don't make bot admin unless required

## 📱 Mobile Management

Koyeb dashboard works on mobile:
1. Access https://app.koyeb.com on phone
2. View logs
3. Restart app
4. Update environment variables

## 💰 Cost Optimization

**Free Tier Limits:**
- 1 app
- 512MB RAM
- $5.50/month worth of resources (free)

**Tips to stay within free tier:**
- Use 1 instance
- Optimize memory usage
- Use external database for large data

## 🆘 Getting Help

**Koyeb Support:**
- [Documentation](https://www.koyeb.com/docs)
- [Community Discord](https://discord.gg/koyeb)
- [Status Page](https://status.koyeb.com/)

**Bot Issues:**
- Check bot logs in Koyeb
- Review GitHub repository
- Test locally first

## 📋 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Koyeb account created
- [ ] Repository connected
- [ ] Environment variables added
- [ ] Dockerfile configured
- [ ] Bot deployed successfully
- [ ] Bot online in Discord
- [ ] Commands working
- [ ] Logs checked for errors
- [ ] Auto-deployment tested

## 🎉 Success!

Your bot should now be running 24/7 on Koyeb!

**Next Steps:**
- Invite bot to your server
- Test all features
- Monitor logs regularly
- Update code as needed

---

## 🔗 Useful Links

- [Koyeb Dashboard](https://app.koyeb.com/)
- [Koyeb Documentation](https://www.koyeb.com/docs)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Bot Repository](https://github.com/yourusername/MeowDow)

---

**Need help?** Create an issue on GitHub or join our Discord server!

**Happy Hosting! 🚀**
