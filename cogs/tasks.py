import discord
from discord.ext import commands, tasks
import utils
from utils.constants import Constants

Ranks = Constants.Ranks


class TaskCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.role_updater.start()

    # Assign the appropriate roles for people depending on their XP
    @tasks.loop(seconds=7.0)
    async def role_updater(self):

        daddy_server = await self.client.fetch_guild(1021919859203903488)

        rank1 = daddy_server.get_role(Ranks.RANK_1_ID)
        rank2 = daddy_server.get_role(Ranks.RANK_2_ID)
        rank3 = daddy_server.get_role(Ranks.RANK_3_ID)
        rank4 = daddy_server.get_role(Ranks.RANK_4_ID)
        rank5 = daddy_server.get_role(Ranks.RANK_5_ID)

        async for member in daddy_server.fetch_members(limit=None):
            xp = utils.xp.get_amount(member)

            if not xp:
                continue

            if xp < Ranks.RANK_1:
                if member.get_role(Ranks.RANK_1_ID):
                    await member.remove_roles(rank1, reason="Lost too much XP to remain ranked")
                    await member.send("You lost Rank I because you don't have enough XP.")

            if Ranks.RANK_1 <= xp < Ranks.RANK_2:
                # Member should have rank but doesn't
                if not member.get_role(Ranks.RANK_1_ID):
                    await member.add_roles(rank1)
                    await member.send("Congratulations! You got Rank I in the Daddy Server!")

            elif Ranks.RANK_2 <= xp < Ranks.RANK_3:
                # Member should have rank but doesn't
                if not member.get_role(Ranks.RANK_2_ID):
                    await member.add_roles(rank2)
                    await member.send("Congratulations! You got Rank II in the Daddy Server!")

            elif Ranks.RANK_3 <= xp < Ranks.RANK_4:
                # Member should have rank but doesn't
                if not member.get_role(Ranks.RANK_3_ID):
                    await member.add_roles(rank3)
                    await member.send("Congratulations! You got Rank III in the Daddy Server!")

            elif Ranks.RANK_4 <= xp < Ranks.RANK_5:
                # Member should have rank but doesn't
                if not member.get_role(Ranks.RANK_4_ID):
                    await member.add_roles(rank4)
                    await member.send("Congratulations! You got Rank IV in the Daddy Server!")

            elif xp >= Ranks.RANK_5:
                # Member should have rank but doesn't
                if not member.get_role(Ranks.RANK_5_ID):
                    await member.add_roles(rank5)
                    await member.send("DAMN BRO... You got Rank V in the Daddy Server!")