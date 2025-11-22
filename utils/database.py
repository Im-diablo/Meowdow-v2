"""
Database handler using aiosqlite for async operations
"""
import aiosqlite
import os
from typing import Optional, List, Tuple, Any
from config import Config

class Database:
    """Async database handler"""
    
    def __init__(self, db_path: str = Config.DATABASE_PATH):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
        
    async def connect(self):
        """Connect to the database"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        await self.create_tables()
        
    async def close(self):
        """Close the database connection"""
        if self.conn:
            await self.conn.close()
            
    async def create_tables(self):
        """Create all necessary tables"""
        async with self.conn.cursor() as cursor:
            # Server settings table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS server_settings (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT DEFAULT '.',
                    welcome_channel_id INTEGER,
                    log_channel_id INTEGER,
                    muted_role_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User profiles table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER,
                    guild_id INTEGER,
                    balance INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0,
                    messages INTEGER DEFAULT 0,
                    last_daily TIMESTAMP,
                    last_weekly TIMESTAMP,
                    last_work TIMESTAMP,
                    last_xp TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            
            # Moderation cases table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS mod_cases (
                    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    action TEXT,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Warnings table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    warning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Economy items table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS shop_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    name TEXT,
                    description TEXT,
                    price INTEGER,
                    role_id INTEGER,
                    stock INTEGER DEFAULT -1
                )
            """)
            
            # User inventory table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_inventory (
                    user_id INTEGER,
                    guild_id INTEGER,
                    item_id INTEGER,
                    quantity INTEGER DEFAULT 1,
                    PRIMARY KEY (user_id, guild_id, item_id)
                )
            """)
            
            await self.conn.commit()
    
    # Server Settings Methods
    async def get_server_prefix(self, guild_id: int) -> str:
        """Get custom prefix for a server"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT prefix FROM server_settings WHERE guild_id = ?",
                (guild_id,)
            )
            result = await cursor.fetchone()
            return result['prefix'] if result else Config.PREFIX
    
    async def set_server_prefix(self, guild_id: int, prefix: str):
        """Set custom prefix for a server"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO server_settings (guild_id, prefix)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET prefix = ?
            """, (guild_id, prefix, prefix))
            await self.conn.commit()
    
    # User Profile Methods
    async def get_user_profile(self, user_id: int, guild_id: int) -> Optional[aiosqlite.Row]:
        """Get user profile"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM user_profiles WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            return await cursor.fetchone()
    
    async def create_user_profile(self, user_id: int, guild_id: int):
        """Create a new user profile"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                INSERT OR IGNORE INTO user_profiles (user_id, guild_id)
                VALUES (?, ?)
            """, (user_id, guild_id))
            await self.conn.commit()
    
    async def update_balance(self, user_id: int, guild_id: int, amount: int):
        """Update user balance"""
        await self.create_user_profile(user_id, guild_id)
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                UPDATE user_profiles
                SET balance = balance + ?
                WHERE user_id = ? AND guild_id = ?
            """, (amount, user_id, guild_id))
            await self.conn.commit()
    
    async def update_xp(self, user_id: int, guild_id: int, xp: int):
        """Update user XP"""
        await self.create_user_profile(user_id, guild_id)
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                UPDATE user_profiles
                SET xp = xp + ?, messages = messages + 1, last_xp = CURRENT_TIMESTAMP
                WHERE user_id = ? AND guild_id = ?
            """, (xp, user_id, guild_id))
            await self.conn.commit()
    
    async def get_leaderboard(self, guild_id: int, field: str = "xp", limit: int = 10) -> List[aiosqlite.Row]:
        """Get leaderboard for a specific field"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(f"""
                SELECT user_id, {field}
                FROM user_profiles
                WHERE guild_id = ?
                ORDER BY {field} DESC
                LIMIT ?
            """, (guild_id, limit))
            return await cursor.fetchall()
    
    # Moderation Methods
    async def add_mod_case(self, guild_id: int, user_id: int, moderator_id: int, action: str, reason: str) -> int:
        """Add a moderation case"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO mod_cases (guild_id, user_id, moderator_id, action, reason)
                VALUES (?, ?, ?, ?, ?)
            """, (guild_id, user_id, moderator_id, action, reason))
            await self.conn.commit()
            return cursor.lastrowid
    
    async def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
        """Add a warning"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
            """, (guild_id, user_id, moderator_id, reason))
            await self.conn.commit()
            return cursor.lastrowid
    
    async def get_warnings(self, guild_id: int, user_id: int) -> List[aiosqlite.Row]:
        """Get all warnings for a user"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM warnings
                WHERE guild_id = ? AND user_id = ?
                ORDER BY created_at DESC
            """, (guild_id, user_id))
            return await cursor.fetchall()

# Global database instance
db = Database()
