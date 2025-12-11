"""
MeowDow Discord Bot - Main Entry Point
A feature-rich Discord bot with moderation, music, economy, leveling, and more!
"""
import discord
from discord.ext import commands
import asyncio
import logging
import os
import sys
from collections import defaultdict
import time
from better_profanity import profanity
import requests
from aiohttp import web

# Import configuration
from config import Config
from utils.database import db

# Setup logging
# Ensure data directory exists for logs
os.makedirs('data', exist_ok=True)

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/bot.log'),  # Changed to data/bot.log
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Bot intents
intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.message_content = True

class MeowDowBot(commands.Bot):
    """Custom Bot class"""
    
    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None  # We'll create a custom help command
        )
        self.start_time = time.time()
        self.spam_detector = SpamDetector()
        self.bad_words_filter_enabled = True
        
    async def get_prefix(self, message):
        """Get custom prefix for each server"""
        if not message.guild:
            return Config.PREFIX
        
        try:
            prefix = await db.get_server_prefix(message.guild.id)
            return commands.when_mentioned_or(prefix)(self, message)
        except:
            return commands.when_mentioned_or(Config.PREFIX)(self, message)
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info("Setting up bot...")
        
        # Connect to database
        await db.connect()
        logger.info("Database connected")

        # Start health check server
        await self.start_health_server()

        
        # Load all cogs
        await self.load_cogs()
        
        # Sync slash commands
        try:
            # Sync to all guilds (Global Sync) - might take up to 1 hour
            # synced = await self.tree.sync()
            # logger.info(f"Synced {len(synced)} slash commands globally")
            
            # FAST SYNC: Sync to current guilds immediately
            for guild in self.guilds:
                try:
                    synced = await self.tree.sync(guild=guild)
                    logger.info(f"Synced {len(synced)} commands to guild {guild.id}")
                except Exception as e:
                    logger.warning(f"Failed to sync to guild {guild.id}: {e}")
            
            # Also do a global sync just in case
            await self.tree.sync()
            
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def start_health_server(self):
        """Start a simple web server for health checks"""
        async def handle(request):
            return web.Response(text="OK")

        app = web.Application()
        app.router.add_get('/', handle)
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Use PORT environment variable (required by Koyeb)
        port = int(os.getenv('PORT', '8000'))
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        logger.info(f"Health check server started on port {port}")

    
    async def load_cogs(self):
        """Load all cog files"""
        cogs_dir = "cogs"
        if not os.path.exists(cogs_dir):
            logger.warning(f"Cogs directory '{cogs_dir}' not found")
            return
        
        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f"cogs.{cog_name}")
                    logger.info(f"Loaded cog: {cog_name}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog_name}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        logger.info(f"Bot ID: {self.user.id}")
        logger.info(f"Servers: {len(self.guilds)}")
        logger.info(f"Users: {sum(g.member_count for g in self.guilds)}")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"over {len(self.guilds)} servers | {Config.PREFIX}help"
            )
        )
        
        # Auto-sync commands to all servers
        logger.info("Auto-syncing commands...")
        for guild in self.guilds:
            try:
                synced = await self.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} commands to guild: {guild.name}")
            except Exception as e:
                logger.warning(f"Failed to sync to {guild.name}: {e}")
        
        # Global sync
        try:
            await self.tree.sync()
            logger.info("Global sync complete")
        except Exception as e:
            logger.error(f"Global sync failed: {e}")
    
    async def on_message(self, message):
        """Called when a message is received"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Check for spam
        is_spam = await self.spam_detector.check_spam(message)
        if is_spam:
            return
        
        # Check for bad words
        if self.bad_words_filter_enabled and contains_bad_word(message.content):
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, please watch your language!",
                    delete_after=5
                )
            except:
                pass
            return
        
        # Process commands
        await self.process_commands(message)
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the necessary permissions to execute this command.")
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ This command is on cooldown. Try again in {error.retry_after:.1f}s")
        
        else:
            logger.error(f"Unhandled error in {ctx.command}: {error}", exc_info=error)
            await ctx.send(f"❌ An error occurred: {str(error)}")
    
    async def close(self):
        """Cleanup when bot is shutting down"""
        logger.info("Shutting down bot...")
        await db.close()
        await super().close()

class SpamDetector:
    """Spam detection system"""
    
    def __init__(self):
        self.message_count = defaultdict(int)
        self.last_reset = defaultdict(float)
        self.muted_users = set()
        self.user_messages = defaultdict(list)
        self.THRESHOLD = Config.SPAM_THRESHOLD
        self.TIME_WINDOW = Config.SPAM_TIME_WINDOW
        self.MUTE_DURATION = Config.SPAM_MUTE_DURATION
    
    async def check_spam(self, message):
        """Check if a message is spam"""
        user_id = message.author.id
        current_time = time.time()
        
        # Reset counter if time window has passed
        if current_time - self.last_reset[user_id] > self.TIME_WINDOW:
            self.message_count[user_id] = 0
            self.last_reset[user_id] = current_time
            self.user_messages[user_id] = []
        
        self.message_count[user_id] += 1
        self.user_messages[user_id].append(message)
        
        # Check if threshold exceeded
        if self.message_count[user_id] > self.THRESHOLD:
            if user_id not in self.muted_users:
                await self.mute_user(message)
            return True
        
        return False
    
    async def mute_user(self, message):
        """Mute a user for spamming"""
        user_id = message.author.id
        self.muted_users.add(user_id)
        
        try:
            # Delete spam messages
            for msg in self.user_messages[user_id]:
                try:
                    await msg.delete()
                except:
                    pass
            
            # Get or create muted role
            muted_role = discord.utils.get(message.guild.roles, name="Muted")
            if not muted_role:
                muted_role = await message.guild.create_role(name="Muted")
                for channel in message.guild.channels:
                    await channel.set_permissions(
                        muted_role,
                        send_messages=False,
                        add_reactions=False,
                        speak=False
                    )
            
            # Mute the user
            await message.author.add_roles(muted_role)
            await message.channel.send(
                f"{message.author.mention} has been muted for {self.MUTE_DURATION} seconds due to spamming."
            )
            
            # Wait and unmute
            await asyncio.sleep(self.MUTE_DURATION)
            await message.author.remove_roles(muted_role)
            self.muted_users.remove(user_id)
            await message.channel.send(f"{message.author.mention}'s mute has been lifted.")
            
        except discord.errors.Forbidden:
            await message.channel.send("I don't have permission to mute users.")
        except Exception as e:
            logger.error(f"Error muting user: {e}")

# Bad words filter
def get_bad_words(url):
    """Fetch bad words list from URL"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            words = response.text.split('\n')
            return set(word.strip().lower() for word in words if word.strip())
    except:
        pass
    return set()

# Load bad words
MAIN_BAD_WORDS_URL = "https://raw.githubusercontent.com/RobertJGabriel/Google-profanity-words/master/list.txt"
CUSTOM_BAD_WORDS_URL = "https://raw.githubusercontent.com/phantom-exe/stock/main/custom_bad_words.txt"

MAIN_BAD_WORDS = get_bad_words(MAIN_BAD_WORDS_URL)
CUSTOM_BAD_WORDS = get_bad_words(CUSTOM_BAD_WORDS_URL)
BAD_WORDS = MAIN_BAD_WORDS.union(CUSTOM_BAD_WORDS)
profanity.load_censor_words(BAD_WORDS)

def contains_bad_word(message):
    """Check if message contains bad words"""
    return profanity.contains_profanity(message)

# Main execution
async def main():
    """Main function to run the bot"""
    bot = MeowDowBot()
    
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=e)
    finally:
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
