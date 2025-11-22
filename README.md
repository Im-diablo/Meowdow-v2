# 🐱 MeowDow Discord Bot

A feature-rich, modular Discord bot with music, moderation, economy, leveling, games, and more!

## ✨ Features

### 🎵 Music System
- Play music from YouTube and Spotify
- Queue management (add, remove, skip, clear)
- Volume control
- Loop and shuffle
- Now playing with progress bar
- Search functionality

### 🛡️ Moderation
- Mute/Unmute members
- Kick and Ban/Unban
- Timeout system
- Message purge with filters
- Spam detection and auto-mute
- Bad word filtering
- Warning system
- Moderation case logging

### 💰 Economy System
- Virtual currency
- Daily and weekly rewards
- Work command to earn coins
- Shop system with items
- User inventory
- Trading between users
- Leaderboards

### 📊 Leveling System
- XP gain from messages
- Level up notifications
- Custom rank cards
- Role rewards for levels
- Server leaderboards
- Customizable XP rates

### 🎮 Mini-Games
- Trivia with multiple categories
- Hangman
- Tic-tac-toe
- Connect Four
- Blackjack
- Slots machine
- Rock Paper Scissors

### 🎉 Fun Commands
- Cat facts and pictures
- Jokes and GIFs
- Slap, hug, pat with GIFs
- 8-ball predictions
- Coinflip
- Meme generator

### 🔧 Utility Commands
- Ping (latency check)
- Calculator
- Dice roller
- Random choice
- Poll creator
- Reminder system
- Translate
- Weather

### ℹ️ Information Commands
- User information
- Server statistics
- Bot information
- Avatar display
- Role information
- Channel information

## 📋 Requirements

- Python 3.8 or higher
- FFmpeg (for music functionality)
- Discord Bot Token
- (Optional) Spotify API credentials
- (Optional) Giphy API key

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/MeowDow.git
cd MeowDow
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add to PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
DISCORD_TOKEN=your_bot_token_here
OWNER_ID=your_discord_user_id
BOT_PREFIX=.
GIPHY_API_KEY=your_giphy_key (optional)
SPOTIFY_CLIENT_ID=your_spotify_id (optional)
SPOTIFY_CLIENT_SECRET=your_spotify_secret (optional)
```

### 5. Run the Bot

```bash
python bot.py
```

## 🔑 Getting API Keys

### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a New Application
3. Go to the "Bot" tab
4. Click "Add Bot"
5. Copy the token
6. Enable "Message Content Intent" and "Server Members Intent"

### Spotify API (Optional)
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Copy Client ID and Client Secret

### Giphy API (Optional)
1. Go to [Giphy Developers](https://developers.giphy.com/)
2. Create an app
3. Copy the API key

## 📁 Project Structure

```
MeowDow/
├── bot.py                  # Main bot file (entry point)
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── .env.example           # Environment template
├── Dockerfile             # Docker configuration
├── README.md              # This file
├── DEPLOYMENT.md          # Koyeb deployment guide
├── cogs/                  # Command modules
│   ├── moderation.py      # Moderation commands
│   ├── music.py           # Music system
│   ├── fun.py             # Fun commands
│   ├── utility.py         # Utility commands
│   ├── info.py            # Information commands
│   ├── economy.py         # Economy system
│   ├── leveling.py        # XP and leveling
│   ├── games.py           # Mini-games
│   └── admin.py           # Bot owner commands
├── utils/                 # Utility modules
│   ├── database.py        # Database handler
│   ├── embeds.py          # Embed templates
│   ├── checks.py          # Permission checks
│   └── helpers.py         # Helper functions
└── data/                  # Data storage
    └── bot.db             # SQLite database (auto-created)
```

## 🎮 Command List

### Prefix Commands
All commands can be used with the prefix (default: `.`)

**Utility:**
- `.ping` - Check bot latency
- `.calc <n1> <op> <n2>` - Calculator
- `.roll [sides]` - Roll a dice
- `.coinflip` - Flip a coin
- `.8ball <question>` - Magic 8-ball
- `.choose <options...>` - Random choice

**Fun:**
- `.meow` - Meow!
- `.catfact` / `.cf` - Random cat fact
- `.nekopic` / `.cp` - Random cat picture
- `.joke` - Random joke
- `.gif <search>` - Search for a GIF
- `.slap @user [item]` - Slap someone

**Music:**
- `.join` - Join voice channel
- `.play <query>` - Play music
- `.pause` - Pause music
- `.resume` - Resume music
- `.skip` - Skip current song
- `.stop` - Stop and clear queue
- `.queue` - Show queue
- `.volume <0-100>` - Set volume

**Moderation:**
- `.mute @user [reason]` - Mute a user
- `.unmute @user` - Unmute a user
- `.kick @user [reason]` - Kick a user
- `.ban @user [reason]` - Ban a user
- `.purge <amount>` - Delete messages

### Slash Commands
All commands are also available as slash commands (`/command`)

Use `/help` to see all available slash commands in Discord.

## ⚙️ Configuration

### Custom Prefix
Change the bot prefix per server:
```
/setprefix <new_prefix>
```

### Bot Settings
Edit `config.py` to customize:
- Embed colors
- Music settings (queue size, volume)
- Economy settings (rewards, cooldowns)
- Leveling settings (XP rates)
- Spam detection thresholds

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t meowdow-bot .
```

### Run Container
```bash
docker run -d --name meowdow --env-file .env meowdow-bot
```

## ☁️ Koyeb Deployment (24/7 Hosting)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Koyeb deployment instructions.

**Quick Steps:**
1. Push code to GitHub
2. Create Koyeb account
3. Connect repository
4. Add environment variables
5. Deploy!

## 🔧 Development

### Adding New Commands

1. Create or edit a cog file in `cogs/`
2. Add your command function
3. Reload the cog: `/reload <cog_name>`

Example:
```python
@commands.command(name="hello")
async def hello(self, ctx):
    await ctx.send("Hello, world!")

@app_commands.command(name="hello", description="Say hello")
async def hello_slash(self, interaction: discord.Interaction):
    await interaction.response.send_message("Hello, world!")
```

### Database Access

```python
from utils.database import db

# Get user profile
profile = await db.get_user_profile(user_id, guild_id)

# Update balance
await db.update_balance(user_id, guild_id, amount)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- Create an issue on GitHub
- Join our Discord server: [Link]
- Email: your@email.com

## 🙏 Credits

- **Discord.py** - Discord API wrapper
- **yt-dlp** - YouTube downloader
- **Spotify API** - Music metadata
- **Giphy API** - GIF search

## 📊 Statistics

- **Commands:** 100+
- **Cogs:** 9
- **Features:** Music, Moderation, Economy, Leveling, Games, and more!

---

Made with ❤️ by [Your Name]

**Star ⭐ this repository if you find it useful!**
