import json
import random
import asyncio
import time
import datetime

import requests

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from discord.ui import Button, View

import utils
from utils import Constants

import gpt


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
                     difficulty: Option(str, "Difficulty of the trivia question",
                                        choices=["Easy", "Medium", "Hard"]) = "Medium"):

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
                    await inter.followup.send(f"That's correct! You got some XP and some MemeCoin.")

                    if difficulty == "Easy":
                        utils.xp.add(inter.user, Constants.XPSettings.TRIVIA_CORRECT_EASY,
                                     dev=utils.is_dev(self.client))
                        utils.add_memecoin(inter.user, Constants.MemeCoin.TRIVIA_CORRECT_EASY, self.client)
                    elif difficulty == "Medium":
                        utils.xp.add(inter.user, Constants.XPSettings.TRIVIA_CORRECT_MED, dev=utils.is_dev(self.client))
                        utils.add_memecoin(inter.user, Constants.MemeCoin.TRIVIA_CORRECT_MED, self.client)
                    else:
                        utils.xp.add(inter.user, Constants.XPSettings.TRIVIA_CORRECT_HARD,
                                     dev=utils.is_dev(self.client))
                        utils.add_memecoin(inter.user, Constants.MemeCoin.TRIVIA_CORRECT_HARD, self.client)

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
    async def insult(self, ctx, victim: Option(discord.User, "User to insult, defaults to you.") = None):
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
            await ctx.send("Did you know? We get our doggos from https://dog.ceo.")

    @commands.slash_command(name="fortune-cookie", description="Get your daily fortune.")
    @commands.cooldown(1, 24 * 60 * 60, commands.BucketType.user)
    async def fortune_cookie(self, ctx):
        with open("assets/bot/fortunes/fortunes.json", 'r') as f:
            fortunes = json.load(f)

        em = discord.Embed(title="Today's Fortune", description="Here's today's fortune")
        em.add_field(name="Fortune", value=random.choice(fortunes), inline=False)
        em.add_field(name="Today's Lucky Number", value=random.randint(1, 99), inline=False)
        em.set_footer(text="Not actual fortunes.")

        await ctx.respond(embed=em)

    @commands.slash_command(name="russian-roulette", description="Play some Russian Roulette with me.")
    async def russian_roulette(self, ctx, wager: Option(int, "Amount of MemeCoins to wager") = 0):
        if utils.get_memecoin(ctx.author, self.client) < wager:
            await ctx.respond("You're too poor to play with that wager.")

        class RussianRouletteView(View):
            def __init__(self, author):
                self.author = author
                super().__init__()

            async def interaction_check(self, inter: discord.MessageInteraction) -> bool:
                if inter.user.id != self.author.id:
                    await inter.response.send_message(content="You don't have permission to press this button.",
                                                      ephemeral=True)
                    return False

                return True

            @discord.ui.button(label="Bail", style=discord.ButtonStyle.red)
            async def bail_callback(self, button, interaction):
                pass

        def check(inter):
            print(inter.data)
            return inter.data["component_type"] == 2 and inter.message.id == game_msg.id

        playing = True

        await ctx.respond(f"Started a game of Russian Roulette with a wager of **{wager}** MemeCoins.")
        game_msg = await ctx.send("Get ready for Russian Roulette!")

        while playing:

            for i in range(1, random.randint(3, 4)):
                await game_msg.edit("You spin the barrel.")
                await asyncio.sleep(0.2)
                await game_msg.edit("You spin the barrel..")
                await asyncio.sleep(0.2)
                await game_msg.edit("You spin the barrel...")
                await asyncio.sleep(0.2)

            if random.randint(1, 6) == 1:
                await game_msg.edit(
                    f"**BANG! You lost.** You were severely injured, and you paid me **{wager}** MemeCoins to be saved.")
                utils.subtract_memecoin(ctx.author, wager, self.client)
                break
            else:
                await game_msg.edit("The Memevolver fired a blank.")

            await asyncio.sleep(3)

            # Do the same for the bot

            await game_msg.edit("I spin the barrel...")
            await asyncio.sleep(3)

            if random.randint(1, 6) == 1:
                await game_msg.edit(f"**BANG! You won.** Here's your **{wager}** MemeCoins. You got some XP as well.")
                utils.add_memecoin(ctx.author, wager, self.client)
                utils.xp.add(ctx.author, Constants.XPSettings.RUS_ROULETTE_XP, dev=utils.is_dev(self.client))
                break
            else:
                await game_msg.edit("The Memevolver fired a blank.")

            await game_msg.edit(content="Moving to the next round... (5s)", view=RussianRouletteView(ctx.author))

            try:
                inter = await self.client.wait_for("interaction", check=check, timeout=5)
                await game_msg.edit("The game was bailed.")
                break
            except asyncio.exceptions.TimeoutError:
                pass

            await game_msg.edit(view=None)

    @commands.slash_command(name="fast-math", description="Answer multiplication questions for XP and MemeCoin.")
    async def fast_math(self, ctx, questions: Option(int, "Amount of questions to complete")):
        def check(msg):
            return msg.author.id == ctx.author.id

        await ctx.respond("Five seconds to answer a question: send your answer in the chat.\n"
                          "Takes longer than five seconds? The game will move on.\n"
                          "To abort, send 'abort', any other non-integer message will be counted as wrong")
        await asyncio.sleep(7)

        total_xp = 0
        total_mc = 0
        correct = 0

        streak = 0
        highest_streak = 0

        streak_msg = await ctx.send("Your streak will appear here.")
        game_msg = await ctx.send("There should be a math question here.")

        for i in range(questions):
            num1 = random.randint(1, 12)
            num2 = random.randint(1, 12)


            await game_msg.edit(f"**#{i + 1}** {num1} × {num2}")

            try:
                msg = await self.client.wait_for("message", check=check, timeout=Constants.FAST_MATH_MAX_ANSWER_TIME)
            except asyncio.exceptions.TimeoutError:
                continue

            if msg.content.lower() == 'abort':
                await ctx.send("Aborted the game.")
                return

            if not msg.content.isdigit():
                await msg.delete()
                continue

            player_ans = int(msg.content)
            true_ans = num1 * num2

            if player_ans == true_ans:
                streak += 1
                if streak >= 3:
                    total_xp += round(Constants.XPSettings.FAST_MATH_QUESTION_XP * ((streak * 0.15) + 1))
                    total_mc += round(Constants.MemeCoin.FAST_MATH_QUESTION_MEMECOIN * ((streak * 0.15) + 1))
                    await streak_msg.edit(f"Streak of **{streak}** questions in a row! 🔥")
                else:
                    total_xp += Constants.XPSettings.FAST_MATH_QUESTION_XP
                total_mc += Constants.MemeCoin.FAST_MATH_QUESTION_MEMECOIN
                correct += 1

            else:
                if highest_streak < streak:
                    highest_streak = streak
                streak = 0  # Resets the streak once getting a question wrong

            if highest_streak < streak:
                highest_streak = streak

            await msg.delete()

        await game_msg.delete()

        if correct == questions and questions >= Constants.FAST_MATH_MINIMUM_ACE:
            total_xp += total_xp * Constants.XPSettings.FAST_MATH_ACE_XP
            total_mc += total_mc * Constants.MemeCoin.FAST_MATH_ACE_MEMECOIN
            highest_streak = streak

        utils.xp.add(ctx.author, total_xp, self.client)
        utils.add_memecoin(ctx.author, total_mc, self.client)

        em = discord.Embed(title="Fast Math Recap", description="Your results", timestamp=datetime.datetime.now())
        em.add_field(name="Correct", value=correct, inline=False)
        em.add_field(name="Incorrect", value=questions - correct, inline=False)
        em.add_field(name="Total Questions", value=questions, inline=False)

        if round(correct / questions * 100, 2) != 100:
            em.add_field(name="Percentage", value=str(round(correct / questions * 100, 2)) + '%', inline=False)
        else:
            em.add_field(name="Percentage", value="💯💯💯💯", inline=False)

        em.add_field(name="XP Earnings", value=total_xp, inline=False)
        em.add_field(name="MemeCoin Earnings", value=total_mc, inline=False)
        em.add_field(name="Highest Streak", value=highest_streak, inline=False)

        await ctx.send(embed=em)

    @commands.slash_command(name="useless-fact", description="Learn something you can't live without")
    async def useless_fact(self, ctx):
        r = requests.get("https://uselessfacts.jsph.pl/random.txt?language=en").content.decode()

        await ctx.respond(r)

    @commands.slash_command(name="convo", description="Talk with a bot. Courtesy OpenAI")
    async def convo(self, ctx):
        await gpt.conversation(ctx, self.client)