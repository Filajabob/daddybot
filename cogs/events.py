import json

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
