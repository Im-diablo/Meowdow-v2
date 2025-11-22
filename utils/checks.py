"""
Custom permission checks for commands
"""
from discord.ext import commands
from config import Config
from typing import Callable

def is_owner():
    """Check if the user is the bot owner"""
    async def predicate(ctx):
        return ctx.author.id == Config.OWNER_ID
    return commands.check(predicate)

def is_admin():
    """Check if the user has administrator permissions"""
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

def is_mod():
    """Check if the user has moderation permissions"""
    async def predicate(ctx):
        perms = ctx.author.guild_permissions
        return perms.kick_members or perms.ban_members or perms.manage_messages
    return commands.check(predicate)

def in_voice():
    """Check if the user is in a voice channel"""
    async def predicate(ctx):
        return ctx.author.voice is not None
    return commands.check(predicate)

def bot_in_voice():
    """Check if the bot is in a voice channel"""
    async def predicate(ctx):
        return ctx.voice_client is not None
    return commands.check(predicate)

def same_voice_channel():
    """Check if the user and bot are in the same voice channel"""
    async def predicate(ctx):
        if not ctx.author.voice or not ctx.voice_client:
            return False
        return ctx.author.voice.channel == ctx.voice_client.channel
    return commands.check(predicate)
