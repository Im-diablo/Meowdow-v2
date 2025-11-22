"""
Helper functions for the bot
"""
import discord
import datetime
import re
from typing import Optional, List

def parse_time(time_str: str) -> Optional[datetime.timedelta]:
    """
    Parse a time string into a timedelta object
    Examples: 10m, 1h, 2d, 1w
    """
    time_regex = re.compile(r"(\d+)([smhdw])")
    matches = time_regex.findall(time_str.lower())
    
    if not matches:
        return None
    
    total_seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit == 's':
            total_seconds += value
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 'h':
            total_seconds += value * 3600
        elif unit == 'd':
            total_seconds += value * 86400
        elif unit == 'w':
            total_seconds += value * 604800
    
    return datetime.timedelta(seconds=total_seconds)

def format_time(seconds: int) -> str:
    """Format seconds into a human-readable string"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a progress bar string"""
    if total == 0:
        return "▱" * length
    
    filled = int((current / total) * length)
    empty = length - filled
    
    return "▰" * filled + "▱" * empty

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def format_number(number: int) -> str:
    """Format a number with commas"""
    return "{:,}".format(number)

async def confirm_action(
    ctx,
    message: str,
    timeout: int = 30
) -> bool:
    """
    Ask for confirmation with reactions
    Returns True if confirmed, False otherwise
    """
    confirm_msg = await ctx.send(message)
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    
    def check(reaction, user):
        return (
            user == ctx.author
            and str(reaction.emoji) in ["✅", "❌"]
            and reaction.message.id == confirm_msg.id
        )
    
    try:
        reaction, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=check)
        await confirm_msg.delete()
        return str(reaction.emoji) == "✅"
    except:
        await confirm_msg.delete()
        return False

class Paginator:
    """Simple paginator for embeds"""
    
    def __init__(self, pages: List[discord.Embed], timeout: int = 60):
        self.pages = pages
        self.timeout = timeout
        self.current_page = 0
    
    async def start(self, ctx):
        """Start the paginator"""
        if not self.pages:
            return
        
        if len(self.pages) == 1:
            await ctx.send(embed=self.pages[0])
            return
        
        message = await ctx.send(embed=self.pages[0])
        await message.add_reaction("⬅️")
        await message.add_reaction("❌")
        await message.add_reaction("➡️")
        
        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["⬅️", "➡️", "❌"]
                and reaction.message.id == message.id
            )
        
        while True:
            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add",
                    timeout=self.timeout,
                    check=check
                )
                
                if str(reaction.emoji) == "❌":
                    await message.delete()
                    break
                elif str(reaction.emoji) == "➡️":
                    self.current_page = (self.current_page + 1) % len(self.pages)
                elif str(reaction.emoji) == "⬅️":
                    self.current_page = (self.current_page - 1) % len(self.pages)
                
                await message.edit(embed=self.pages[self.current_page])
                await message.remove_reaction(reaction, user)
                
            except:
                await message.clear_reactions()
                break
