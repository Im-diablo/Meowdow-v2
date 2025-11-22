"""
Information Commands Cog
User info, Server info, Bot info
"""
import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import Embeds
import platform
import time
from datetime import datetime

class Info(commands.Cog):
    """Information commands"""

    def __init__(self, bot):
        self.bot = bot

    # USER INFO
    @commands.command(name="userinfo", aliases=["ui", "whois"], help="Get user information")
    async def userinfo_prefix(self, ctx, member: discord.Member = None):
        """Get user info"""
        member = member or ctx.author
        embed = self.create_user_embed(member)
        await ctx.send(embed=embed)

    @app_commands.command(name="userinfo", description="Get user information")
    @app_commands.describe(member="Member to check")
    async def userinfo_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        """Get user info"""
        member = member or interaction.user
        embed = self.create_user_embed(member)
        await interaction.response.send_message(embed=embed)

    def create_user_embed(self, member):
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        embed = Embeds.create_embed(title=f"User Info: {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Created Account", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(roles) if roles else "None", inline=False)
        return embed

    # SERVER INFO
    @commands.command(name="serverinfo", aliases=["si"], help="Get server information")
    async def serverinfo_prefix(self, ctx):
        """Get server info"""
        embed = self.create_server_embed(ctx.guild)
        await ctx.send(embed=embed)

    @app_commands.command(name="serverinfo", description="Get server information")
    async def serverinfo_slash(self, interaction: discord.Interaction):
        """Get server info"""
        embed = self.create_server_embed(interaction.guild)
        await interaction.response.send_message(embed=embed)

    def create_server_embed(self, guild):
        embed = Embeds.create_embed(title=f"Server Info: {guild.name}")
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="ID", value=guild.id, inline=True)
        return embed

    # AVATAR
    @commands.command(name="avatar", aliases=["av"], help="Get user avatar")
    async def avatar_prefix(self, ctx, member: discord.Member = None):
        """Get avatar"""
        member = member or ctx.author
        embed = discord.Embed(title=f"{member}'s Avatar", color=member.color)
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @app_commands.command(name="avatar", description="Get user avatar")
    @app_commands.describe(member="Member to check")
    async def avatar_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        """Get avatar"""
        member = member or interaction.user
        embed = discord.Embed(title=f"{member}'s Avatar", color=member.color)
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # BOT INFO
    @commands.command(name="botinfo", aliases=["bi", "about"], help="Get bot information")
    async def botinfo_prefix(self, ctx):
        """Get bot info"""
        embed = self.create_bot_embed()
        await ctx.send(embed=embed)

    @app_commands.command(name="botinfo", description="Get bot information")
    async def botinfo_slash(self, interaction: discord.Interaction):
        """Get bot info"""
        embed = self.create_bot_embed()
        await interaction.response.send_message(embed=embed)

    def create_bot_embed(self):
        embed = Embeds.info(
            "A feature-rich Discord bot with music, moderation, economy, and more!",
            title="MeowDow Bot Info"
        )
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=sum(g.member_count for g in self.bot.guilds), inline=True)
        uptime = str(datetime.now() - datetime.fromtimestamp(self.bot.start_time)).split('.')[0]
        embed.add_field(name="Uptime", value=uptime, inline=True)
        return embed

    # JOINED COMMAND
    @commands.command(name="joined", help="Check when a member joined")
    async def joined_prefix(self, ctx, member: discord.Member = None):
        """Check join date"""
        member = member or ctx.author
        await ctx.send(f"**{member}** joined on {member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}")

    @app_commands.command(name="joined", description="Check when a member joined")
    @app_commands.describe(member="Member to check")
    async def joined_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        """Check join date"""
        member = member or interaction.user
        await interaction.response.send_message(f"**{member}** joined on {member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}")

async def setup(bot):
    await bot.add_cog(Info(bot))
