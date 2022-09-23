import discord
from discord.ext import commands


class MiscCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="ping", description="Get the bot's latency")
    async def ping(self, ctx):
        """Get the bot's latency"""
        await ctx.respond(f"Pong! Latency: {round(self.client.latency, 2)}ms")

    @commands.slash_command(name="friend-code", description="Invite a friend for XP")
    async def friend_code(self, ctx):
        pass
