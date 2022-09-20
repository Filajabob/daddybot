import discord
from discord.ext import commands


class EventCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Client logged in as {self.client.user.name}.")
