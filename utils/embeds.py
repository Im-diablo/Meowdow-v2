"""
Embed templates for consistent branding across the bot
"""
import discord
from datetime import datetime
from typing import Optional
from config import Config

class Embeds:
    """Utility class for creating consistent embeds"""
    
    @staticmethod
    def create_embed(
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: int = Config.COLOR_PRIMARY,
        footer: Optional[str] = None,
        timestamp: bool = True
    ) -> discord.Embed:
        """Create a basic embed with consistent styling"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow() if timestamp else None
        )
        
        if footer:
            embed.set_footer(text=footer)
            
        return embed
    
    @staticmethod
    def success(description: str, title: str = "✅ Success") -> discord.Embed:
        """Create a success embed"""
        return Embeds.create_embed(
            title=title,
            description=description,
            color=Config.COLOR_SUCCESS
        )
    
    @staticmethod
    def error(description: str, title: str = "❌ Error") -> discord.Embed:
        """Create an error embed"""
        return Embeds.create_embed(
            title=title,
            description=description,
            color=Config.COLOR_ERROR
        )
    
    @staticmethod
    def warning(description: str, title: str = "⚠️ Warning") -> discord.Embed:
        """Create a warning embed"""
        return Embeds.create_embed(
            title=title,
            description=description,
            color=Config.COLOR_WARNING
        )
    
    @staticmethod
    def info(description: str, title: str = "ℹ️ Information") -> discord.Embed:
        """Create an info embed"""
        return Embeds.create_embed(
            title=title,
            description=description,
            color=Config.COLOR_INFO
        )
    
    @staticmethod
    def music_now_playing(title: str, url: str, requester: discord.Member) -> discord.Embed:
        """Create a now playing embed for music"""
        embed = Embeds.create_embed(
            title="🎵 Now Playing",
            description=f"**[{title}]({url})**",
            color=Config.COLOR_PRIMARY
        )
        embed.set_footer(
            text=f"Requested by {requester.display_name}",
            icon_url=requester.display_avatar.url
        )
        return embed
    
    @staticmethod
    def music_added_to_queue(title: str, position: int) -> discord.Embed:
        """Create an added to queue embed"""
        return Embeds.create_embed(
            title="➕ Added to Queue",
            description=f"**{title}**\nPosition in queue: {position}",
            color=Config.COLOR_INFO
        )
