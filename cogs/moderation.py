"""
Moderation Commands Cog
Kick, Ban, Mute, Purge, etc.
"""
import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import Embeds
from utils.database import db
from typing import Optional

class Moderation(commands.Cog):
    """Moderation commands"""

    def __init__(self, bot):
        self.bot = bot

    # KICK COMMAND
    @commands.command(name="kick", help="Kick a member")
    @commands.has_permissions(kick_members=True)
    async def kick_prefix(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Kick a member"""
        await member.kick(reason=reason)
        embed = Embeds.success(f"**{member}** has been kicked.\nReason: {reason}", title="User Kicked")
        await ctx.send(embed=embed)
        # Log to DB
        await db.add_mod_case(ctx.guild.id, member.id, ctx.author.id, "KICK", reason)

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.describe(member="The member to kick", reason="Reason for kicking")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Kick a member"""
        await member.kick(reason=reason)
        embed = Embeds.success(f"**{member}** has been kicked.\nReason: {reason}", title="User Kicked")
        await interaction.response.send_message(embed=embed)
        await db.add_mod_case(interaction.guild.id, member.id, interaction.user.id, "KICK", reason)

    # BAN COMMAND
    @commands.command(name="ban", help="Ban a member")
    @commands.has_permissions(ban_members=True)
    async def ban_prefix(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Ban a member"""
        await member.ban(reason=reason)
        embed = Embeds.success(f"**{member}** has been banned.\nReason: {reason}", title="User Banned")
        await ctx.send(embed=embed)
        await db.add_mod_case(ctx.guild.id, member.id, ctx.author.id, "BAN", reason)

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.describe(member="The member to ban", reason="Reason for banning")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Ban a member"""
        await member.ban(reason=reason)
        embed = Embeds.success(f"**{member}** has been banned.\nReason: {reason}", title="User Banned")
        await interaction.response.send_message(embed=embed)
        await db.add_mod_case(interaction.guild.id, member.id, interaction.user.id, "BAN", reason)

    # UNBAN COMMAND
    @commands.command(name="unban", help="Unban a user (ID or Name)")
    @commands.has_permissions(ban_members=True)
    async def unban_prefix(self, ctx, *, user_input: str):
        """Unban a user"""
        banned_users = [entry async for entry in ctx.guild.bans()]
        
        user_to_unban = None
        for ban_entry in banned_users:
            user = ban_entry.user
            if str(user.id) == user_input or user.name == user_input:
                user_to_unban = user
                break
        
        if user_to_unban:
            await ctx.guild.unban(user_to_unban)
            embed = Embeds.success(f"**{user_to_unban}** has been unbanned.", title="User Unbanned")
            await ctx.send(embed=embed)
            await db.add_mod_case(ctx.guild.id, user_to_unban.id, ctx.author.id, "UNBAN", "Manual unban")
        else:
            await ctx.send("❌ User not found in ban list.")

    @app_commands.command(name="unban", description="Unban a user")
    @app_commands.describe(user_id="The ID of the user to unban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_slash(self, interaction: discord.Interaction, user_id: str):
        """Unban a user"""
        try:
            user_obj = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user_obj)
            embed = Embeds.success(f"**{user_obj}** has been unbanned.", title="User Unbanned")
            await interaction.response.send_message(embed=embed)
            await db.add_mod_case(interaction.guild.id, user_obj.id, interaction.user.id, "UNBAN", "Manual unban")
        except discord.NotFound:
            await interaction.response.send_message("❌ User not found.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    # TIMEOUT / MUTE COMMAND
    @commands.command(name="mute", aliases=["timeout"], help="Timeout a member")
    @commands.has_permissions(moderate_members=True)
    async def mute_prefix(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        """Timeout a member"""
        from utils.helpers import parse_time
        delta = parse_time(duration)
        if not delta:
            await ctx.send("❌ Invalid duration format. Use 10m, 1h, 1d etc.")
            return
            
        await member.timeout(delta, reason=reason)
        embed = Embeds.success(f"**{member}** has been muted for {duration}.\nReason: {reason}", title="User Muted")
        await ctx.send(embed=embed)
        await db.add_mod_case(ctx.guild.id, member.id, ctx.author.id, "MUTE", reason)

    @app_commands.command(name="mute", description="Timeout a member")
    @app_commands.describe(member="Member to mute", duration="Duration (e.g. 10m, 1h)", reason="Reason")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute_slash(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        """Timeout a member"""
        from utils.helpers import parse_time
        delta = parse_time(duration)
        if not delta:
            await interaction.response.send_message("❌ Invalid duration format. Use 10m, 1h, 1d etc.", ephemeral=True)
            return
            
        await member.timeout(delta, reason=reason)
        embed = Embeds.success(f"**{member}** has been muted for {duration}.\nReason: {reason}", title="User Muted")
        await interaction.response.send_message(embed=embed)
        await db.add_mod_case(interaction.guild.id, member.id, interaction.user.id, "MUTE", reason)

    # PURGE COMMAND
    @commands.command(name="purge", aliases=["clear"], help="Delete messages")
    @commands.has_permissions(manage_messages=True)
    async def purge_prefix(self, ctx, amount: int):
        """Delete messages"""
        deleted = await ctx.channel.purge(limit=amount + 1) # +1 to include command message
        await ctx.send(f"🧹 Deleted {len(deleted)-1} messages.", delete_after=3)

    @app_commands.command(name="purge", description="Delete messages")
    @app_commands.describe(amount="Number of messages to delete")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge_slash(self, interaction: discord.Interaction, amount: int):
        """Delete messages"""
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
