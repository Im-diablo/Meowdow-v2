"""
Configuration management for MeowDow Bot
Handles environment variables and bot settings
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Bot configuration class"""
    
    # Bot Settings
    PREFIX: str = os.getenv("BOT_PREFIX", ".")
    OWNER_ID: Optional[int] = None
    
    # Parse OWNER_ID safely
    try:
        if os.getenv("OWNER_ID"):
            OWNER_ID = int(os.getenv("OWNER_ID"))
    except ValueError:
        print(f"Warning: OWNER_ID must be a numeric Discord user ID, not '{os.getenv('OWNER_ID')}'")
        print("To get your Discord user ID:")
        print("1. Enable Developer Mode in Discord (Settings > Advanced > Developer Mode)")
        print("2. Right-click your username and select 'Copy User ID'")
        print("3. Update OWNER_ID in your .env file with this number")
        OWNER_ID = None
    
    # API Keys
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    GIPHY_API_KEY: str = os.getenv("GIPHY_API_KEY", "")
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    
    # Embed Colors (Hex)
    COLOR_PRIMARY: int = 0x00b29f  # Teal
    COLOR_SUCCESS: int = 0x00ff00  # Green
    COLOR_ERROR: int = 0xff0000    # Red
    COLOR_WARNING: int = 0xffaa00  # Orange
    COLOR_INFO: int = 0x3498db     # Blue
    
    # Music Settings
    MUSIC_MAX_QUEUE_SIZE: int = 100
    MUSIC_DEFAULT_VOLUME: float = 0.5
    MUSIC_TIMEOUT: int = 300  # 5 minutes of inactivity
    
    # Moderation Settings
    SPAM_THRESHOLD: int = 5
    SPAM_TIME_WINDOW: int = 5  # seconds
    SPAM_MUTE_DURATION: int = 60  # seconds
    
    # Economy Settings
    ECONOMY_DAILY_REWARD: int = 100
    ECONOMY_WEEKLY_REWARD: int = 1000
    ECONOMY_WORK_MIN: int = 50
    ECONOMY_WORK_MAX: int = 200
    ECONOMY_WORK_COOLDOWN: int = 3600  # 1 hour
    
    # Leveling Settings
    XP_PER_MESSAGE: int = 10
    XP_COOLDOWN: int = 60  # 1 minute between XP gains
    XP_MULTIPLIER: float = 1.0
    
    # Database
    DATABASE_PATH: str = "data/bot.db"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is required in environment variables")
        return True

# Validate configuration on import
Config.validate()
