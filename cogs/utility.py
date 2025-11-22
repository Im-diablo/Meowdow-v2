"""
Utility Commands Cog
Includes: ping, calculator, roll, random, poll, etc.
"""
import discord
from discord.ext import commands
from discord import app_commands
import random
from utils.embeds import Embeds
from config import Config

class Utility(commands.Cog):
    """Utility commands for the bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # PING COMMAND
    @commands.command(name="ping", help="Check bot latency")
    async def ping_prefix(self, ctx):
        """Prefix version of ping"""
        latency = round(self.bot.latency * 1000)
        embed = Embeds.info(
            f"🏓 Pong! Latency: **{latency}ms**",
            title="Ping"
        )
        await ctx.send(embed=embed)
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping_slash(self, interaction: discord.Interaction):
        """Slash version of ping"""
        latency = round(self.bot.latency * 1000)
        embed = Embeds.info(
            f"🏓 Pong! Latency: **{latency}ms**",
            title="Ping"
        )
        await interaction.response.send_message(embed=embed)
    
    # CALCULATOR COMMAND
    @commands.command(name="calc", aliases=["calculate"], help="Calculate two numbers")
    async def calc_prefix(self, ctx, n1: float, operation: str, n2: float):
        """Prefix calculator"""
        result = await self._calculate(n1, n2, operation)
        if isinstance(result, str):
            await ctx.send(result)
        else:
            await ctx.send(f"**Result:** `{result}`")
    
    @app_commands.command(name="calculator", description="Calculate two numbers")
    @app_commands.describe(
        n1="First number",
        n2="Second number",
        operation="Operation (+ - * / ^ %)"
    )
    async def calc_slash(self, interaction: discord.Interaction, n1: float, n2: float, operation: str):
        """Slash calculator"""
        result = await self._calculate(n1, n2, operation)
        if isinstance(result, str):
            await interaction.response.send_message(result, ephemeral=True)
        else:
            await interaction.response.send_message(f"**Result:** `{result}`")
    
    async def _calculate(self, n1: float, n2: float, operation: str):
        """Calculate operation"""
        operations = {
            "+": lambda: n1 + n2,
            "-": lambda: n1 - n2,
            "*": lambda: n1 * n2,
            "/": lambda: n1 / n2 if n2 != 0 else "Cannot divide by zero",
            "^": lambda: n1 ** n2,
            "%": lambda: n1 % n2 if n2 != 0 else "Cannot modulo by zero"
        }
        
        if operation not in operations:
            return "Invalid operation. Use: + - * / ^ %"
        
        return operations[operation]()
    
    # ROLL DICE COMMAND
    @commands.command(name="roll", help="Roll a dice")
    async def roll_prefix(self, ctx, sides: int = 6):
        """Roll a dice"""
        result = random.randint(1, sides)
        await ctx.send(f"🎲 You rolled a **{result}**! (1-{sides})")
    
    @app_commands.command(name="roll", description="Roll a dice")
    @app_commands.describe(sides="Number of sides (default: 6)")
    async def roll_slash(self, interaction: discord.Interaction, sides: int = 6):
        """Roll a dice"""
        result = random.randint(1, sides)
        await interaction.response.send_message(f"🎲 You rolled a **{result}**! (1-{sides})")
    
    # RANDOM CHOICE COMMAND
    @commands.command(name="choose", aliases=["random"], help="Choose randomly from options")
    async def choose_prefix(self, ctx, *choices):
        """Choose randomly"""
        if not choices:
            await ctx.send("Please provide choices!")
            return
        choice = random.choice(choices)
        await ctx.send(f"🎯 I choose: **{choice}**")
    
    # COINFLIP COMMAND
    @commands.command(name="coinflip", aliases=["flip"], help="Flip a coin")
    async def coinflip_prefix(self, ctx):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        await ctx.send(f"🪙 The coin landed on: **{result}**!")
    
    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip_slash(self, interaction: discord.Interaction):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"🪙 The coin landed on: **{result}**!")
    
    # 8BALL COMMAND
    @commands.command(name="8ball", help="Ask the magic 8ball")
    async def eightball_prefix(self, ctx, *, question: str):
        """Magic 8ball"""
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        response = random.choice(responses)
        embed = Embeds.create_embed(
            title="🎱 Magic 8-Ball",
            description=f"**Question:** {question}\n**Answer:** {response}",
            color=Config.COLOR_PRIMARY
        )
        await ctx.send(embed=embed)
    
    @app_commands.command(name="8ball", description="Ask the magic 8ball")
    @app_commands.describe(question="Your question")
    async def eightball_slash(self, interaction: discord.Interaction, question: str):
        """Magic 8ball"""
        responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        response = random.choice(responses)
        embed = Embeds.create_embed(
            title="🎱 Magic 8-Ball",
            description=f"**Question:** {question}\n**Answer:** {response}",
            color=Config.COLOR_PRIMARY
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
