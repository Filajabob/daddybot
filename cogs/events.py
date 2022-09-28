import json
import random

import datetime
import discord
from discord.ext import commands

import pytz

from utils.constants import Constants


class EventCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Client logged in as {self.client.user.name}.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        em = discord.Embed(title="Hello Newbie!", description="Welcome to the Daddy Server!")
        em.add_field(name="About Me", value="I am the main bot in this server. I have many features, and more are"
                                            "coming.")
        em.add_field(name="XP", value="Being active on the server can get you XP. XP can get you to rank up, unlocking "
                                      "exclusive channels and commands.")
        em.add_field(name="Get a Code?", value="Did you get a code when you were invited? Run /claim <code> to claim"
                                               "the code and get XP. Make sure to do it quick, if you take too long,"
                                               "you'll never be able to claim a code again.")
        await member.send(embed=em)

        # Give child role to member
        await member.add_roles(member.guild.get_role(1021965016976605316))

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f'Slow down! You can use this command in {round(error.retry_after, 2)} seconds.')
            return

        await ctx.respond(f"Something went wrong! Error: {error}", ephemeral=True)

        bot_error_channel = await self.client.fetch_channel(1024057742496911420)
        now = datetime.datetime.now(pytz.UTC)
        now_strftime = now.strftime("%Y-%m-%d %H:%M:%S")

        em = discord.Embed(title=f"{type(error).__name__} at {now_strftime} UTC", color=discord.Color.red(),
                           timestamp=now)
        em.add_field(name="Traceback", value=str(error), inline=False)
        em.add_field(name="User", value=ctx.author.mention, inline=False)
        em.add_field(name="Channel", value=ctx.channel.mention, inline=False)
        em.add_field(name="Timestamp", value=now_strftime, inline=False)

        await bot_error_channel.send(embed=em)

        raise error

    @commands.Cog.listener()
    async def on_message(self, msg):
        # We got a message sent by the bot
        if msg.author.id == self.client.user.id:
            return

        # We don't care if a bot sends a message
        if msg.author.bot:
            return

        # Add XP to the author's total XP
        with open("assets/bot/xp/xp.json", 'r+') as f:
            data = json.load(f)

            if str(msg.author.id) not in data:
                data[str(msg.author.id)] = Constants.XPSettings.MESSAGE_XP
            else:
                data[str(msg.author.id)] += Constants.XPSettings.MESSAGE_XP

            f.seek(0)
            json.dump(data, f)
            f.truncate()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        msgs = ["Here comes {}..!", "{} joined the game.", "I was hoping for Ryan Reynolds, but here's {}.",
                "Hello {}! Hope you brought snacks.", ""]

        updates = await self.client.fetch_channel(1022328541217566760)

        await updates.send(random.choice(msgs).replace('{}', member.mention))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        msgs = ["There goes {}. I never liked them anyway.", "Hey hey hey, goodbye {}", "{} left the game.",
                "{} abandoned the match, and won't be spawned this round. Or ever. Unless they come back."]

        updates = await self.client.fetch_channel(1022328541217566760)

        await updates.send(random.choice(msgs).replace('{}', member.mention))
