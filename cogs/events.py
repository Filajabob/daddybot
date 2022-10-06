import json
import random
import logging
import traceback

import datetime
import discord
from discord.ext import commands

import pytz

import utils
from utils.constants import Constants

error_logs = logging.getLogger('errors')
error_logs.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='logs/errors.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(name)s: %(message)s'))
error_logs.addHandler(handler)


class EventCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Client logged in as {self.client.user.name}.")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f'Slow down! You can use this command in {round(error.retry_after, 2)} seconds.')
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.respond(f"Don't overstep boundaries! {str(error)}")
            return

        await ctx.respond(f"Something went wrong! Error: {error}", ephemeral=True)

        error_logs.error("".join(traceback.format_exception(error)))

        bot_error_channel = await self.client.fetch_channel(1024057742496911420)
        now = datetime.datetime.now(pytz.UTC)
        now_strftime = now.strftime("%Y-%m-%d %H:%M:%S")

        em = discord.Embed(title=f"{type(error).__name__} at {now_strftime} UTC", color=discord.Color.red(),
                           timestamp=now)
        em.add_field(name="Traceback", value=str(error), inline=False)
        em.add_field(name="User", value=ctx.author.mention, inline=False)
        em.add_field(name="Command", value=ctx.command.name, inline=False)
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
        utils.xp.add(msg.author, Constants.XPSettings.MESSAGE_XP, dev=utils.is_dev(self.client))

        # Add to statistics
        utils.log_msg(msg, self.client)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        utils.log_member_join(member, self.client)

        em = discord.Embed(title="Hello Newbie!", description="Welcome to **Memetopia**!")
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

        # Send hello message
        msgs = ["Here comes {}..!", "{} joined the game.", "I was hoping for Ryan Reynolds, but here's {}.",
                "Hello {}! Hope you brought snacks.", "Ello there {}.", "Wazzup {}!", "Hey look, its {}!", "{} is here."
                " Did you bring snacks by chance?", "Hi {}. Hopefully your name doesn't look weird with this sentence."]

        updates = await self.client.fetch_channel(1022328541217566760)

        await updates.send(random.choice(msgs).replace('{}', member.mention))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        utils.log_member_leave(member, self.client)

        msgs = ["There goes {}. I never liked them anyway.", "Hey hey hey, goodbye {}", "{} left the game.",
                "{} abandoned the match, and won't be spawned this round. Or ever. Unless they come back.",
                "Hey {} left. Here's a song that matches the vibe: <https://www.youtube.com/watch?v=jsaTElBljOE>"]

        updates = await self.client.fetch_channel(1022328541217566760)

        await updates.send(random.choice(msgs).replace('{}', member.mention))

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        em = discord.Embed(title=f"{message.author.name}'s message got deleted",
                              description="", timestamp=datetime.datetime.now(), color=discord.Color.red())
        em.add_field(name="Message", value=f"||{message.content}||", inline=False)

        channel = await self.client.fetch_channel(1026665929335119914)
        await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_message_edit(self, msg_before, msg_after):
        em = discord.Embed(title=f"{msg_before.author.name} edited a message", timestamp=datetime.datetime.now(),
                           color=discord.Color.blue())
        em.add_field(name="Before", value=f"||{msg_before.content}||", inline=False)
        em.add_field(name="After", value=msg_after.content, inline=False)

        channel = await self.client.fetch_channel(1026665929335119914)
        await channel.send(embed=em)