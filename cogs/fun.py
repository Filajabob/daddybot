import json
import random

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup

import requests


class FunCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    quote = SlashCommandGroup("quote", "Get a quote")

    @quote.command(name="breaking-bad", description="Get a quote from the TV show Breaking Bad")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def breaking_bad(self, ctx):
        url = "https://www.breakingbadapi.com/api/quote/random"
        r = json.loads(requests.get(url).content.decode())

        await ctx.respond(f"{r[0]['quote']}\n-{r[0]['author']}")

    @quote.command(name="the-office", description="Get a quote from the TV show The Office (US)")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def the_office(self, ctx):
        with open("assets/bot/quotes/the-office/the-office-quotes.json", 'r') as f:
            data = json.load(f)

        quote = random.choice(data)
        await ctx.respond(f"{quote['quote']}\n-{quote['character']}")