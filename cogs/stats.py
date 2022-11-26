import datetime

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option

import utils
from utils import Constants

class StatsCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    stats = SlashCommandGroup("stats", "Check the stats of any supported category")

    @stats.command(name="messages", description="Get message stats. Ranked members only.")
    async def stats_messages(self, ctx):
        if utils.xp.get_amount(ctx.author, utils.is_dev(self.client)) < Constants.Ranks.RANK_1:
            raise commands.MissingPermissions("You must be ranked to use this command.")

        await ctx.respond(f"{utils.get_msg_stats(self.client)} messages were sent today.")

    @stats.command(name="member-change", description="Get member join/leave stats. Ranked members only.")
    async def stats_member_change(self, ctx):
        if utils.xp.get_amount(ctx.author, utils.is_dev(self.client)) < Constants.Ranks.RANK_1:
            raise commands.MissingPermissions("You must be ranked to use this command.")

        change = utils.get_member_join_stats(self.client) - utils.get_member_leave_stats(self.client)

        if change >= 0:
            change = f"+{change}"

        em = discord.Embed(title="Member Change Today", timestamp=datetime.datetime.now())
        em.add_field(name="Member Joins", value=str(utils.get_member_join_stats(self.client)), inline=False)
        em.add_field(name="Member Leaves", value=str(utils.get_member_leave_stats(self.client)), inline=False)
        em.add_field(name="Change", value=change, inline=False)
        em.set_footer(text="Including kicks/bans. Some join/leave events may not be included due to downtime.")

        await ctx.respond(embed=em)

    @stats.command(name="vc-time", description="Get time spent in VCs. Ranked members only.")
    async def vc_time(self, ctx):
        if utils.xp.get_amount(ctx.author, utils.is_dev(self.client)) < Constants.Ranks.RANK_1:
            raise commands.MissingPermissions("You must be ranked to use this command.")

        await ctx.respond(str(datetime.timedelta(seconds=utils.get_vc_seconds(self.client))))