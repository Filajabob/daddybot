import json
import random
import datetime

import discord
from discord.ext import commands, tasks
import pytz

import utils
from utils.constants import Constants

Ranks = Constants.Ranks


class TaskCog(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.role_updater.start()
        self.presence_updater.start()
        self.daily_xp.start()

    # Assign the appropriate roles for people depending on their XP
    @tasks.loop(seconds=7.0)
    async def role_updater(self):
        await self.client.wait_until_ready()

        if utils.is_dev(self.client): return

        memetopia = await self.client.fetch_guild(1021919859203903488)

        rank1 = memetopia.get_role(Ranks.RANK_1_ID)
        rank2 = memetopia.get_role(Ranks.RANK_2_ID)
        rank3 = memetopia.get_role(Ranks.RANK_3_ID)
        rank4 = memetopia.get_role(Ranks.RANK_4_ID)
        rank5 = memetopia.get_role(Ranks.RANK_5_ID)

        async for member in memetopia.fetch_members(limit=None):
            xp = utils.xp.get_amount(member, dev=utils.is_dev(self.client))

            if not xp:
                continue

            if xp < Ranks.RANK_1:
                if member.get_role(Ranks.RANK_1_ID):
                    await member.remove_roles(rank1, rank2, rank3, rank4, rank5, reason="Lost too much XP to remain ranked")
                    await member.send("You lost Rank I because you don't have enough XP.")

            if Ranks.RANK_1 <= xp < Ranks.RANK_2:
                # Member should have rank 1 but doesn't
                if not member.get_role(Ranks.RANK_1_ID):
                    await member.add_roles(rank1)
                    await member.remove_roles(rank2, rank3, rank4, rank5)
                    await member.send("Congratulations! You got Rank I in Memetopia!")

            elif Ranks.RANK_2 <= xp < Ranks.RANK_3:
                # Member should have rank 2 but doesn't
                if not member.get_role(Ranks.RANK_2_ID):
                    await member.add_roles(rank2)
                    await member.remove_roles(rank1, rank3, rank4, rank5)
                    await member.send("Congratulations! You got Rank II in Memetopia!")

            elif Ranks.RANK_3 <= xp < Ranks.RANK_4:
                # Member should have rank but doesn't
                if not member.get_role(Ranks.RANK_3_ID):
                    await member.add_roles(rank3)
                    await member.remove_roles(rank1, rank2, rank4, rank5)
                    await member.send("Congratulations! You got Rank III in Memetopia!")

            elif Ranks.RANK_4 <= xp < Ranks.RANK_5:
                # Member should have rank but doesn't
                if not member.get_role(Ranks.RANK_4_ID):
                    await member.add_roles(rank4)
                    await member.remove_roles(rank1, rank2, rank3, rank5)
                    await member.send("Congratulations! You got Rank IV in Memetopia!")

            elif xp >= Ranks.RANK_5:
                # Member should have rank but doesn't
                if not member.get_role(Ranks.RANK_5_ID):
                    await member.add_roles(rank5)
                    await member.remove_roles(rank1, rank2, rank3, rank4)
                    await member.send("DAMN BRO... You got Rank V in Memetopia! What the-")

    @tasks.loop(minutes=5)
    async def presence_updater(self):
        await self.client.wait_until_ready()
        memetopia = await self.client.fetch_guild(1021919859203903488)
        members = await memetopia.fetch_members().flatten()

        with open("assets/bot/presences/presences.json", 'r') as f:
            data = json.load(f)

        presence_category = random.choice(["gaming", "listening", "watching"])

        if presence_category == "gaming":
            activity = discord.Game(name=random.choice(data[presence_category]).replace("{ran member}",
                                                                                       f"@{random.choice(members).name}"))

        elif presence_category == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening,
                                        name=random.choice(data[presence_category]).replace("{ran member}",
                                                                                       f"@{random.choice(members).name}"))

        else:
            activity = discord.Activity(type=discord.ActivityType.watching,
                                        name=random.choice(data[presence_category]).replace("{ran member}",
                                                                                       f"@{random.choice(members).name}"))

        await self.client.change_presence(activity=activity)

    # Run every day at midnight EST, or 4 AM UTC
    @tasks.loop(time=datetime.time(4, 0, 0))
    async def daily_xp(self):
        await self.client.wait_until_ready()
        memetopia = await self.client.fetch_guild(1021919859203903488)

        async for member in memetopia.fetch_members(limit=None):
            utils.xp.add(member, Constants.XPSettings.DAILY_XP, dev=utils.is_dev(self.client))

