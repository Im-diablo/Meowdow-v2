"""
Fun Commands Cog
Jokes, Memes, Animals, etc.
"""
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
from utils.embeds import Embeds
from config import Config

class Fun(commands.Cog):
    """Fun commands"""

    def __init__(self, bot):
        self.bot = bot

    # MEOW COMMAND
    @commands.command(name="meow", help="Meow!")
    async def meow_prefix(self, ctx):
        """Meow!"""
        await ctx.send("Meow! 🐱")

    @app_commands.command(name="meow", description="Meow!")
    async def meow_slash(self, interaction: discord.Interaction):
        """Meow!"""
        await interaction.response.send_message("Meow! 🐱")

    # CAT FACT COMMAND
    @commands.command(name="catfact", aliases=["cf"], help="Get a random cat fact")
    async def catfact_prefix(self, ctx):
        """Get cat fact"""
        fact = await self.get_cat_fact()
        await ctx.send(f"🐱 **Cat Fact:** {fact}")

    @app_commands.command(name="catfact", description="Get a random cat fact")
    async def catfact_slash(self, interaction: discord.Interaction):
        """Get cat fact"""
        fact = await self.get_cat_fact()
        await interaction.response.send_message(f"🐱 **Cat Fact:** {fact}")

    async def get_cat_fact(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://catfact.ninja/fact") as resp:
                data = await resp.json()
                return data.get("fact", "Cats are awesome!")

    # JOKE COMMAND
    @commands.command(name="joke", help="Get a random joke")
    async def joke_prefix(self, ctx):
        """Get joke"""
        setup, punchline = await self.get_joke()
        await ctx.send(f"😂 **{setup}**\n||{punchline}||")

    @app_commands.command(name="joke", description="Get a random joke")
    async def joke_slash(self, interaction: discord.Interaction):
        """Get joke"""
        setup, punchline = await self.get_joke()
        await interaction.response.send_message(f"😂 **{setup}**\n||{punchline}||")

    async def get_joke(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://official-joke-api.appspot.com/random_joke") as resp:
                data = await resp.json()
                return data.get("setup", "Why did the chicken cross the road?"), data.get("punchline", "To get to the other side!")

    # SLAP COMMAND
    @commands.command(name="slap", help="Slap someone")
    async def slap_prefix(self, ctx, member: discord.Member):
        """Slap someone"""
        gif = random.choice([
            "https://media.giphy.com/media/Gf3AUz3eBNbSXOEbs4/giphy.gif",
            "https://media.giphy.com/media/xT9IgzFnSqzt2Sp3QA/giphy.gif",
            "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif"
        ])
        embed = discord.Embed(description=f"**{ctx.author.mention} slapped {member.mention}!** 👋", color=Config.COLOR_PRIMARY)
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

    @app_commands.command(name="slap", description="Slap someone")
    @app_commands.describe(member="Person to slap")
    async def slap_slash(self, interaction: discord.Interaction, member: discord.Member):
        """Slap someone"""
        gif = random.choice([
            "https://media.giphy.com/media/Gf3AUz3eBNbSXOEbs4/giphy.gif",
            "https://media.giphy.com/media/xT9IgzFnSqzt2Sp3QA/giphy.gif",
            "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif"
        ])
        embed = discord.Embed(description=f"**{interaction.user.mention} slapped {member.mention}!** 👋", color=Config.COLOR_PRIMARY)
        embed.set_image(url=gif)
        await interaction.response.send_message(embed=embed)

    # GIF COMMAND
    @commands.command(name="gif", help="Search for a GIF")
    async def gif_prefix(self, ctx, *, query: str):
        """Search GIF"""
        url = await self.get_gif(query)
        if url:
            await ctx.send(url)
        else:
            await ctx.send("❌ No GIF found.")

    @app_commands.command(name="gif", description="Search for a GIF")
    @app_commands.describe(query="Search term")
    async def gif_slash(self, interaction: discord.Interaction, query: str):
        """Search GIF"""
        url = await self.get_gif(query)
        if url:
            await interaction.response.send_message(url)
        else:
            await interaction.response.send_message("❌ No GIF found.", ephemeral=True)

    async def get_gif(self, query):
        if not Config.GIPHY_API_KEY:
            return "https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif" # Default if no key
            
        async with aiohttp.ClientSession() as session:
            url = f"https://api.giphy.com/v1/gifs/search?api_key={Config.GIPHY_API_KEY}&q={query}&limit=1&rating=g"
            async with session.get(url) as resp:
                data = await resp.json()
                if data['data']:
                    return data['data'][0]['images']['original']['url']
                return None

    # CAT PIC COMMAND
    @commands.command(name="nekopic", aliases=["cp", "catpic"], help="Get a random cat picture")
    async def catpic_prefix(self, ctx):
        """Get cat picture"""
        url = await self.get_cat_pic()
        embed = discord.Embed(title="🐱 Here's a cat!", color=Config.COLOR_PRIMARY)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @app_commands.command(name="catpic", description="Get a random cat picture")
    async def catpic_slash(self, interaction: discord.Interaction):
        """Get cat picture"""
        url = await self.get_cat_pic()
        embed = discord.Embed(title="🐱 Here's a cat!", color=Config.COLOR_PRIMARY)
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed)

    async def get_cat_pic(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search") as resp:
                data = await resp.json()
                if data:
                    return data[0]['url']
                return "https://cataas.com/cat"

    # SAY COMMAND
    @commands.command(name="say", help="Make the bot say something")
    @commands.has_permissions(manage_messages=True)
    async def say_prefix(self, ctx, *, message: str):
        """Make bot say something"""
        await ctx.message.delete()
        await ctx.send(message)

    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.describe(message="Message to say")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say_slash(self, interaction: discord.Interaction, message: str):
        """Make bot say something"""
        await interaction.response.send_message("Sent!", ephemeral=True)
        await interaction.channel.send(message)

async def setup(bot):
    await bot.add_cog(Fun(bot))
