import json
import random

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option

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

    @commands.slash_command(name="search-pi", description="Search for a series of digits in Pi.")
    async def search_pi(self, ctx, search):
        url = "https://introcs.cs.princeton.edu/java/data/pi-10million.txt"
        r = requests.get(url).content.decode()

        digit = r.find(search)

        if digit == -1:
            await ctx.respond(f"{search} was not found within the first ten million digits of Pi.")
            return


        await ctx.respond(f"**{search}** starts at digit **{digit + 2}**.\n")

        if (not digit - 5 <= 0) and (not digit + 5 > len(r)):
            await ctx.send(f"...{r[digit - 5:digit]}**{search}**{r[digit + len(search):digit + len(search) + 5]}...")


