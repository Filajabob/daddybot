# ALL THIS CODE WAS TAKEN FROM HERE: https://stackoverflow.com/a/66630462/19106293

import discord
from discord.ext import commands
from discord.ui import View
import random
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
import youtube_dl
from youtube_dl import YoutubeDL

import utils

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.duration = data.get('duration')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            if len(data['entries']) > 0:
                data = data['entries'][0]

        embed = discord.Embed(title="",
                              description=f"Queued [{data['title']}]({data['webpage_url']}) [{ctx.author.mention}]",
                              color=discord.Color.green())
        await ctx.respond(embed=embed)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            embed = discord.Embed(title="Now playing",
                                  description=f"[{source.title}]({source.web_url}) [{source.requester.mention}]",
                                  color=discord.Color.green())
            self.np = await self._channel.send(embed=embed)
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class MusicCog(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.respond('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.respond('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.slash_command(name='join', aliases=['connect', 'j'], description="connects to voice")
    async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                embed = discord.Embed(title="",
                                      description="No channel to join. Please call `/join` from a voice channel.",
                                      color=discord.Color.green())
                await ctx.respond(embed=embed)
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')
        if random.randint(0, 1) == 0:
            await ctx.respond('👍')
        await ctx.respond(f'**Joined `{channel}`**')

    @commands.slash_command(name='play', aliases=['sing', 'p'], description="streams music")
    async def play_(self, ctx, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)

    @commands.slash_command(name='pause', description="pauses music")
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            embed = discord.Embed(title="", description="I am currently not playing anything",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.respond("Paused ⏸️")

    @commands.slash_command(name='resume', description="resumes music")
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.respond("Resuming ⏯️")

    @commands.slash_command(name='skip', description="Skips to next song in queue. Members below Rank 4 must /vote-skip")
    async def skip_(self, ctx):
        """Skip the song."""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()

        await ctx.respond("Skipping...")

    @commands.slash_command(name="vote-skip", description="Set up a poll to skip the current playing song")
    async def vote_skip(self, ctx):
        client = self.bot
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        voted = []

        class VoteSkipView(View):
            def __init(self):
                self.timeout = 60
                self.disable_on_timeout = True

                super().__init__()

            async def interaction_check(self, inter: discord.MessageInteraction) -> bool:
                if inter.user.id in voted:
                    await inter.response.send_message(content="You already voted!",
                                                      ephemeral=True)
                    return False
                return True

            @discord.ui.button(style=discord.ButtonStyle.green, emoji="⏩")
            async def skip_callback(self, button, inter):
                voted.append(inter.user.id)
                await inter.response.send_message(content="Voted!",
                                                  ephemeral=True)

                em = discord.Embed(title="Vote Skip", description="Vote to skip this song")
                em.add_field(name="Vote Skip alert!", value="Click the button below to vote in favour of skipping.")
                em.set_footer(text=f"Votes: {len(voted)} ⏩")

                await inter.followup.edit_message(message_id=inter.message.id, embed=em)

                if len(voted) >= utils.Constants.REQUIRED_VOTES_TO_SKIP:
                    await inter.followup.edit_message(message_id=inter.message.id, content="The vote was successful. This song will be skipped.",
                                                      embed=None, view=None)

                    if not vc or not vc.is_connected():
                        embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                              color=discord.Color.green())
                        return await ctx.respond(embed=embed)

                    if vc.is_paused():
                        pass
                    elif not vc.is_playing():
                        return

                    vc.stop()


        em = discord.Embed(title="Vote Skip", description="Vote to skip this song")
        em.add_field(name="Vote Skip alert!", value="Click the button below to vote in favour of skipping.")
        em.set_footer(text="Votes: 0 ⏩")

        vote_msg = await ctx.respond(embed=em, view=VoteSkipView())

        def check(inter):
            print(inter.data)
            return inter.data["component_type"] == 2 and inter.message.id == vote_msg.id


    @commands.slash_command(name='remove', aliases=['rm', 'rem'], description="removes specified song from queue")
    async def remove_(self, ctx, pos: int = None):
        """Removes specified song from queue"""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        player = self.get_player(ctx)
        if pos == None:
            player.queue._queue.pop()
        else:
            try:
                s = player.queue._queue[pos - 1]
                del player.queue._queue[pos - 1]
                embed = discord.Embed(title="",
                                      description=f"Removed [{s['title']}]({s['webpage_url']}) [{s['requester'].mention}]",
                                      color=discord.Color.green())
                await ctx.respond(embed=embed)
            except:
                embed = discord.Embed(title="", description=f'Could not find a track for "{pos}"',
                                      color=discord.Color.green())
                await ctx.respond(embed=embed)

    @commands.slash_command(name='clear', aliases=['clr', 'cl', 'cr'], description="clears entire queue")
    async def clear_(self, ctx):
        """Deletes entire queue of upcoming songs."""

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        player = self.get_player(ctx)
        player.queue._queue.clear()
        await ctx.respond('💣 **Cleared**')

    @commands.slash_command(name='queue', aliases=['q', 'playlist', 'que'], description="shows the queue")
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        player = self.get_player(ctx)
        if player.queue.empty():
            embed = discord.Embed(title="", description="queue is empty", color=discord.Color.green())
            return await ctx.respond(embed=embed)

        seconds = vc.source.duration % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        # Grabs the songs in the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))
        fmt = '\n'.join(
            f"`{(upcoming.index(_)) + 1}.` [{_['title']}]({_['webpage_url']}) | ` {duration} Requested by: {_['requester']}`\n"
            for _ in upcoming)
        fmt = f"\n__Now Playing__:\n[{vc.source.title}]({vc.source.web_url}) | ` {duration} Requested by: {vc.source.requester}`\n\n__Up Next:__\n" + fmt + f"\n**{len(upcoming)} songs in queue**"
        embed = discord.Embed(title=f'Queue for {ctx.guild.name}', description=fmt, color=discord.Color.green())
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        await ctx.respond(embed=embed)

    @commands.slash_command(name='now-playing', aliases=['song', 'current', 'current-song', 'playing'],
                      description="shows the current playing song")
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        player = self.get_player(ctx)
        if not player.current:
            embed = discord.Embed(title="", description="I am currently not playing anything",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        seconds = vc.source.duration % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)

        embed = discord.Embed(title="",
                              description=f"[{vc.source.title}]({vc.source.web_url}) [{vc.source.requester.mention}] | `{duration}`",
                              color=discord.Color.green())
        embed.set_author(name=f"Now Playing 🎶")
        await ctx.respond(embed=embed)

    @commands.slash_command(name='volume', aliases=['vol', 'v'], description="changes DaddyBot's volume")
    async def change_volume(self, ctx, *, vol: float=None):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I am not currently connected to voice",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        if not vol:
            embed = discord.Embed(title="", description=f"🔊 **{vc.source.volume * 100}%**",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        if not 0 < vol < 101:
            embed = discord.Embed(title="", description="Please enter a value between 1 and 100",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        embed = discord.Embed(title="", description=f'**`{ctx.author}`** set the volume to **{vol}%**',
                              color=discord.Color.green())
        await ctx.respond(embed=embed)

    @commands.slash_command(name='stop', aliases=["leave", "dc", "disconnect", "bye"],
                      description="stops music and disconnects from voice")
    async def stop_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            embed = discord.Embed(title="", description="I'm not connected to a voice channel",
                                  color=discord.Color.green())
            return await ctx.respond(embed=embed)

        if (random.randint(0, 1) == 0):
            await ctx.respond('👋')
        await ctx.respond('**Successfully disconnected**')

        await self.cleanup(ctx.guild)