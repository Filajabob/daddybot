import json
import random

import requests

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from discord.ui import Button, View

import utils
from utils import Constants


class FunCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    quote = SlashCommandGroup("quote", "Get a quote")

    @quote.command(name="breaking-bad", description="Get a quote from the TV show Breaking Bad")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def breaking_bad(self, ctx):
        url = "https://www.breakingbadapi.com/api/quote/random"
        r = json.loads(requests.get(url).content.decode())

        await ctx.respond(f"{r[0]['quote']}\n-{r[0]['author']}")

    @quote.command(name="the-office", description="Get a quote from the TV show The Office (US)")
    @commands.cooldown(1, 10, commands.BucketType.user)
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

    @commands.slash_command(name="trivia", description="Answer trivia, get XP.")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def trivia(self, ctx,
                     difficulty: Option(str, "Difficulty of the trivia question", choices=["Easy", "Medium", "Hard"])):

        if difficulty == "Easy":
            url = "https://opentdb.com/api.php?amount=1&difficulty=easy&type=boolean"
        elif difficulty == "Medium":
            url = "https://opentdb.com/api.php?amount=1&difficulty=medium&type=boolean"
        elif difficulty == "Hard":
            url = "https://opentdb.com/api.php?amount=1&difficulty=hard&type=boolean"

        r = json.loads(requests.get(url).content.decode())["results"][0]

        class RestrictedView(View):
            def __init__(self, author):
                self.author = author
                super().__init__()

            async def interaction_check(self, inter: discord.MessageInteraction) -> bool:
                if inter.user.id != self.author.id:
                    await inter.response.send_message(content="You don't have permission to press this button.",
                                                  ephemeral=True)
                    return False

                self.disable_all_items()
                await inter.response.edit_message(view=view)

                return True

        class TriviaButton(Button):
            def __init__(self, label, style):
                super().__init__(label=label, style=style)
                self.content = label

            async def callback(self, inter):
                if r['correct_answer'] == self.content:
                    await inter.followup.send(f"That's correct! You got some XP.")

                    if difficulty == "Easy":
                        utils.xp.add(inter.user, Constants.XPSettings.TRIVIA_CORRECT_EASY, dev=utils.is_dev(self.client))
                    elif difficulty == "Medium":
                        utils.xp.add(inter.user, Constants.XPSettings.TRIVIA_CORRECT_MED, dev=utils.is_dev(self.client))
                    else:
                        utils.xp.add(inter.user, Constants.XPSettings.TRIVIA_CORRECT_HARD, dev=utils.is_dev(self.client))

                else:
                    await inter.followup.send("That's wroooong! LOL")

        view = RestrictedView(ctx.author)
        view.add_item(TriviaButton(label="True", style=discord.ButtonStyle.green))
        view.add_item(TriviaButton(label="False", style=discord.ButtonStyle.red))

        em = discord.Embed(title="Trivia!", description=r['category'])
        em.add_field(name="Question", value=r['question'].replace("&quot;", '"'))

        await ctx.respond(embed=em, view=view)

    @commands.slash_command(name="insult", description="Get insulted by the bot or insult someone else")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def insult(self, ctx, victim: Option(discord.User, "User to insult, defaults to you.")=None):
        url = "https://evilinsult.com/generate_insult.php?lang=en&type=json"
        insult = json.loads(requests.get(url).content.decode())["insult"]

        if not victim:
            await ctx.respond(insult)
        else:
            try:
                await victim.send(f"{insult}\nDelivered by {ctx.author.mention}")
                await ctx.respond(f"{victim.mention} has been insulted!")
            except discord.Forbidden:
                await ctx.respond("The insult couldn't be delivered due to the victim's DM settings.", ephemeral=True)
                return

        if random.randint(0, 6) == 1:
            await ctx.send("Did you know? We get our insults from https://evilinsult.com.")

    @commands.slash_command(name="doggo", description="Dogs are far superior to cats")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def doggo(self, ctx):
        url = "https://dog.ceo/api/breeds/image/random"
        dog = json.loads(requests.get(url).content.decode())["message"]

        await ctx.respond(dog)

        if random.randint(0, 6) == 1:
            await ctx.send("Did you know? We get our insults from https://dog.ceo.")

    @commands.slash_command(name="fortune-cookie", description="Get your daily fortune.")
    @commands.cooldown(1, 24 * 60 * 60, commands.BucketType.user)
    async def fortune_cookie(self, ctx):
        with open("assets/bot/fortunes/fortunes.json", 'r') as f:
            fortunes = json.load(f)

        em = discord.Embed(title="Today's Fortune", description="Here's today's fortune", inline=False)
        em.add_field(name="Fortune", value=random.choice(fortunes), inline=False)
        em.add_field(name="Today's Lucky Number", value=random.randint(1, 99))
        em.set_footer(text="Not actual fortunes.")

        await ctx.respond(embed=em)