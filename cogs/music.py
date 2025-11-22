"""
Music Commands Cog
Handles music playback from YouTube and Spotify
"""
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
from utils.embeds import Embeds
from config import Config
from typing import Optional

# YTDL Options
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': 'data/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

class Music(commands.Cog):
    """Music commands for playing songs"""

    def __init__(self, bot):
        self.bot = bot
        self.queues = {} # Guild ID -> List of songs
        self.current_song = {} # Guild ID -> Current song title

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    async def play_next(self, ctx):
        if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
            # Get next song
            url, title = self.queues[ctx.guild.id].pop(0)
            self.current_song[ctx.guild.id] = title
            
            async with ctx.typing():
                try:
                    player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                    ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                    
                    embed = Embeds.music_now_playing(title, url, ctx.author)
                    await ctx.send(embed=embed)
                except Exception as e:
                    await ctx.send(f"An error occurred playing the next song: {e}")
                    self.current_song[ctx.guild.id] = None
        else:
            self.current_song[ctx.guild.id] = None
            # Disconnect if queue is empty? Maybe not immediately.

    @commands.command(name="join", help="Join the voice channel")
    async def join_prefix(self, ctx):
        """Join voice channel"""
        if not ctx.author.voice:
            await ctx.send("❌ You are not connected to a voice channel.")
            return
        
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        
        await channel.connect(self_deaf=True)
        await ctx.send(f"✅ Joined {channel.mention}")

    @app_commands.command(name="join", description="Join the voice channel")
    async def join_slash(self, interaction: discord.Interaction):
        """Join voice channel"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You are not connected to a voice channel.", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.move_to(channel)
            await interaction.response.send_message(f"✅ Moved to {channel.mention}")
        else:
            await channel.connect(self_deaf=True)
            await interaction.response.send_message(f"✅ Joined {channel.mention}")

    @commands.command(name="play", aliases=["p"], help="Play a song")
    async def play_prefix(self, ctx, *, query: str):
        """Play a song"""
        if not ctx.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect(self_deaf=True)
            else:
                await ctx.send("❌ You need to be in a voice channel!")
                return

        async with ctx.typing():
            try:
                # Basic search if not a URL
                if not query.startswith("http"):
                    query = f"ytsearch:{query}"

                # Extract info but don't download yet
                info = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
                
                if 'entries' in info:
                    info = info['entries'][0]
                
                url = info['webpage_url']
                title = info['title']
                
                queue = self.get_queue(ctx.guild.id)
                
                if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                    queue.append((url, title))
                    embed = Embeds.music_added_to_queue(title, len(queue))
                    await ctx.send(embed=embed)
                else:
                    self.queues[ctx.guild.id] = [(url, title)] # Initialize/Reset queue with this song
                    await self.play_next(ctx)
                    
            except Exception as e:
                await ctx.send(f"❌ An error occurred: {e}")

    @app_commands.command(name="play", description="Play a song from YouTube")
    @app_commands.describe(query="Song name or URL")
    async def play_slash(self, interaction: discord.Interaction, query: str):
        """Play a song"""
        await interaction.response.defer()
        
        if not interaction.guild.voice_client:
            if interaction.user.voice:
                await interaction.user.voice.channel.connect(self_deaf=True)
            else:
                await interaction.followup.send("❌ You need to be in a voice channel!")
                return

        try:
            # Basic search if not a URL
            search_query = query
            if not query.startswith("http"):
                search_query = f"ytsearch:{query}"

            # Extract info
            info = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False))
            
            if 'entries' in info:
                info = info['entries'][0]
            
            url = info['webpage_url']
            title = info['title']
            
            queue = self.get_queue(interaction.guild.id)
            
            # We need a context-like object for play_next
            # Creating a fake context is tricky, so we'll adapt play_next or duplicate logic
            # For simplicity in this quick implementation, we'll duplicate the logic slightly or use a helper
            
            if interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
                queue.append((url, title))
                embed = Embeds.music_added_to_queue(title, len(queue))
                await interaction.followup.send(embed=embed)
            else:
                queue.append((url, title))
                # Trigger playback
                # We need to call play_next but it expects ctx. 
                # Let's manually trigger the first song here for slash command
                
                url_to_play, title_to_play = queue.pop(0)
                self.current_song[interaction.guild.id] = title_to_play
                
                player = await YTDLSource.from_url(url_to_play, loop=self.bot.loop, stream=True)
                
                # We need a way to call play_next recursively. 
                # We can create a dummy class with necessary attributes
                class DummyContext:
                    def __init__(self, guild, voice_client, bot, author, send):
                        self.guild = guild
                        self.voice_client = voice_client
                        self.bot = bot
                        self.author = author
                        self.send = send
                        self.typing = lambda: asyncio.sleep(0) # Dummy context manager

                dummy_ctx = DummyContext(
                    interaction.guild, 
                    interaction.guild.voice_client, 
                    self.bot, 
                    interaction.user, 
                    lambda embed=None, **kwargs: interaction.channel.send(embed=embed, **kwargs)
                )

                interaction.guild.voice_client.play(
                    player, 
                    after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(dummy_ctx), self.bot.loop)
                )
                
                embed = Embeds.music_now_playing(title_to_play, url_to_play, interaction.user)
                await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {e}")

    @commands.command(name="skip", help="Skip the current song")
    async def skip_prefix(self, ctx):
        """Skip song"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped!")
        else:
            await ctx.send("❌ Nothing is playing.")

    @app_commands.command(name="skip", description="Skip the current song")
    async def skip_slash(self, interaction: discord.Interaction):
        """Skip song"""
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped!")
        else:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

    @commands.command(name="stop", help="Stop music and clear queue")
    async def stop_prefix(self, ctx):
        """Stop music"""
        self.queues[ctx.guild.id] = []
        self.current_song[ctx.guild.id] = None
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
        await ctx.send("cx Stopped music and cleared queue.")

    @app_commands.command(name="stop", description="Stop music and clear queue")
    async def stop_slash(self, interaction: discord.Interaction):
        """Stop music"""
        self.queues[interaction.guild.id] = []
        self.current_song[interaction.guild.id] = None
        if interaction.guild.voice_client:
            interaction.guild.voice_client.stop()
            await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Stopped music and cleared queue.")

    @commands.command(name="queue", aliases=["q"], help="Show the current queue")
    async def queue_prefix(self, ctx):
        """Show queue"""
        queue = self.get_queue(ctx.guild.id)
        if not queue and not self.current_song.get(ctx.guild.id):
            await ctx.send("The queue is empty.")
            return

        desc = ""
        if self.current_song.get(ctx.guild.id):
            desc += f"**Now Playing:** {self.current_song[ctx.guild.id]}\n\n"
        
        if queue:
            desc += "**Up Next:**\n"
            for i, (url, title) in enumerate(queue[:10], 1):
                desc += f"{i}. {title}\n"
            if len(queue) > 10:
                desc += f"\n...and {len(queue) - 10} more"
        
        embed = Embeds.info(desc, title="Music Queue")
        await ctx.send(embed=embed)

    @app_commands.command(name="queue", description="Show the current queue")
    async def queue_slash(self, interaction: discord.Interaction):
        """Show queue"""
        queue = self.get_queue(interaction.guild.id)
        if not queue and not self.current_song.get(interaction.guild.id):
            await interaction.response.send_message("The queue is empty.", ephemeral=True)
            return

        desc = ""
        if self.current_song.get(interaction.guild.id):
            desc += f"**Now Playing:** {self.current_song[interaction.guild.id]}\n\n"
        
        if queue:
            desc += "**Up Next:**\n"
            for i, (url, title) in enumerate(queue[:10], 1):
                desc += f"{i}. {title}\n"
            if len(queue) > 10:
                desc += f"\n...and {len(queue) - 10} more"
        
        embed = Embeds.info(desc, title="Music Queue")
        await interaction.response.send_message(embed=embed)

    # PAUSE COMMAND
    @commands.command(name="pause", help="Pause the current song")
    async def pause_prefix(self, ctx):
        """Pause music"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused!")
        else:
            await ctx.send("❌ Nothing is playing.")

    @app_commands.command(name="pause", description="Pause the current song")
    async def pause_slash(self, interaction: discord.Interaction):
        """Pause music"""
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("⏸️ Paused!")
        else:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

    # RESUME COMMAND
    @commands.command(name="resume", help="Resume the current song")
    async def resume_prefix(self, ctx):
        """Resume music"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed!")
        else:
            await ctx.send("❌ Nothing is paused.")

    @app_commands.command(name="resume", description="Resume the current song")
    async def resume_slash(self, interaction: discord.Interaction):
        """Resume music"""
        if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("▶️ Resumed!")
        else:
            await interaction.response.send_message("❌ Nothing is paused.", ephemeral=True)

    # VOLUME COMMAND
    @commands.command(name="volume", aliases=["vol"], help="Set volume (0-100)")
    async def volume_prefix(self, ctx, volume: int):
        """Set volume"""
        if not ctx.voice_client:
            return await ctx.send("❌ Not connected.")
        
        if 0 <= volume <= 100:
            ctx.voice_client.source.volume = volume / 100
            await ctx.send(f"🔊 Volume set to {volume}%")
        else:
            await ctx.send("❌ Volume must be between 0 and 100")

    @app_commands.command(name="volume", description="Set volume (0-100)")
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume_slash(self, interaction: discord.Interaction, volume: int):
        """Set volume"""
        if not interaction.guild.voice_client:
            return await interaction.response.send_message("❌ Not connected.", ephemeral=True)
        
        if 0 <= volume <= 100:
            interaction.guild.voice_client.source.volume = volume / 100
            await interaction.response.send_message(f"🔊 Volume set to {volume}%")
        else:
            await interaction.response.send_message("❌ Volume must be between 0 and 100", ephemeral=True)

    # REMOVE COMMAND
    @commands.command(name="remove", help="Remove a song from queue")
    async def remove_prefix(self, ctx, index: int):
        """Remove song"""
        queue = self.get_queue(ctx.guild.id)
        if 1 <= index <= len(queue):
            removed = queue.pop(index - 1)
            await ctx.send(f"🗑️ Removed **{removed[1]}** from queue.")
        else:
            await ctx.send("❌ Invalid queue index.")

    @app_commands.command(name="remove", description="Remove a song from queue")
    @app_commands.describe(index="Position in queue")
    async def remove_slash(self, interaction: discord.Interaction, index: int):
        """Remove song"""
        queue = self.get_queue(interaction.guild.id)
        if 1 <= index <= len(queue):
            removed = queue.pop(index - 1)
            await interaction.response.send_message(f"🗑️ Removed **{removed[1]}** from queue.")
        else:
            await interaction.response.send_message("❌ Invalid queue index.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Music(bot))
