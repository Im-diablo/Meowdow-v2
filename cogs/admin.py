"""
Admin Commands Cog
Owner-only commands for bot management
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
from utils.embeds import Embeds
from config import Config

class Admin(commands.Cog):
    """Admin commands for bot owners"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def is_owner(self, user_id: int) -> bool:
        """Check if user is the bot owner"""
        return user_id == Config.OWNER_ID or user_id == self.bot.owner_id
    
    @commands.command(name="sync", help="Sync slash commands (Owner only)")
    async def sync_prefix(self, ctx, scope: Optional[str] = None):
        """Sync slash commands"""
        if not self.is_owner(ctx.author.id):
            await ctx.send("❌ This command is owner-only!")
            return
        
        try:
            if scope == "guild" or scope == "server":
                # Sync to current guild only (instant)
                synced = await self.bot.tree.sync(guild=ctx.guild)
                await ctx.send(f"✅ Synced {len(synced)} commands to this server!")
            elif scope == "global":
                # Sync globally (takes up to 1 hour)
                synced = await self.bot.tree.sync()
                await ctx.send(f"✅ Synced {len(synced)} commands globally (may take up to 1 hour to appear)")
            else:
                # Sync to current guild by default
                synced = await self.bot.tree.sync(guild=ctx.guild)
                await ctx.send(f"✅ Synced {len(synced)} commands to this server!")
        except Exception as e:
            await ctx.send(f"❌ Failed to sync: {e}")
    
    @commands.command(name="reload", help="Reload a cog (Owner only)")
    async def reload_prefix(self, ctx, cog: str):
        """Reload a cog"""
        if not self.is_owner(ctx.author.id):
            await ctx.send("❌ This command is owner-only!")
            return
        
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Reloaded cog: `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload `{cog}`: {e}")
    
    @commands.command(name="load", help="Load a cog (Owner only)")
    async def load_prefix(self, ctx, cog: str):
        """Load a cog"""
        if not self.is_owner(ctx.author.id):
            await ctx.send("❌ This command is owner-only!")
            return
        
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Loaded cog: `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to load `{cog}`: {e}")
    
    @commands.command(name="unload", help="Unload a cog (Owner only)")
    async def unload_prefix(self, ctx, cog: str):
        """Unload a cog"""
        if not self.is_owner(ctx.author.id):
            await ctx.send("❌ This command is owner-only!")
            return
        
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f"✅ Unloaded cog: `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to unload `{cog}`: {e}")
    
    @commands.command(name="cogs", aliases=["listcogs"], help="List all loaded cogs")
    async def cogs_prefix(self, ctx):
        """List all loaded cogs"""
        cogs = [cog for cog in self.bot.cogs]
        embed = Embeds.info(
            "\n".join([f"• {cog}" for cog in cogs]) if cogs else "No cogs loaded",
            title=f"Loaded Cogs ({len(cogs)})"
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="servers", aliases=["guilds"], help="List all servers (Owner only)")
    async def servers_prefix(self, ctx):
        """List all servers the bot is in"""
        if not self.is_owner(ctx.author.id):
            await ctx.send("❌ This command is owner-only!")
            return
        
        guilds = self.bot.guilds
        guild_list = "\n".join([f"• {guild.name} ({guild.id}) - {guild.member_count} members" for guild in guilds[:10]])
        
        if len(guilds) > 10:
            guild_list += f"\n\n...and {len(guilds) - 10} more"
        
        embed = Embeds.info(
            guild_list,
            title=f"Servers ({len(guilds)})"
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
