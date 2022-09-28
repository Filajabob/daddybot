import json
import random
import string
import datetime
import pytz

import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

import utils
from utils.constants import Constants

Ranks = Constants.Ranks

class MiscCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    xp = SlashCommandGroup("xp", "XP-related things")

    @commands.slash_command(name="invite", description="Get the server's offical vanity link")
    async def invite(self, ctx):
        await ctx.respond("<https://dsc.gg/daddy-server>")

    @commands.slash_command(name="ping", description="Get the bot's latency")
    async def ping(self, ctx):
        """Get the bot's latency"""
        await ctx.respond(f"Pong! Latency: {round(self.client.latency, 2)}ms")

    @commands.slash_command(name="reset-codes", description="Reset all your codes. No going back!")
    async def reset_codes(self, ctx):
        code_json = "assets/bot/friend_code/codes.json"

        with open(code_json, 'r+') as f:
            data = json.load(f)
            data[str(ctx.author.id)] = []

            f.seek(0)
            json.dump(data, f)
            f.truncate()

        await ctx.respond("Codes have been reset.", ephemeral=True)

    @commands.slash_command(name="friend-code", description="Generate a code that you can send to a friend when you "
                                                            "invite them. /friend-code-help **")
    async def friend_code(self, ctx):
        code_json = "assets/bot/friend_code/codes.json"

        with open(code_json, 'r') as f:
            data = json.load(f)

        alphabet = list(string.ascii_lowercase)
        code = ""

        while True:
            for i in range(6):
                code += random.choice(alphabet)

            for user, codes in data.items():
                if code in codes:
                    break
            else:
                break

        with open(code_json, 'r+') as f:
            data = json.load(f)

            if str(ctx.author.id) in data:
                if len(data[str(ctx.author.id)]) >= 3:
                    await ctx.respond("You can only have 3 codes at once. To reset your codes, run /reset-codes",
                                      ephemeral=True)
                    return

                data[str(ctx.author.id)].append(code)
            else:
                data[str(ctx.author.id)] = [code]

            f.seek(0)
            json.dump(data, f)
            f.truncate()

        await ctx.respond(f"Your friend code has been created. Keep it safe! Code: **{code}**\n"
                          f"Make sure they claim the code as soon as they join.", ephemeral=True)

    @commands.slash_command(name="friend-code-help", description="Confused about friend codes? Here's the place!")
    async def friend_code_help(self, ctx):
        await ctx.respond("Friend codes are a way to reward those who invite people to promote server growth. Share your "
                          "code with a friend while inviting them and you and your friend will earn XP! **Your friend must claim"
                                                            f"the code within {Constants.MAX_CLAIM_TIME} seconds of "
                                                            f"joining with /claim.**")

    @commands.slash_command(name="claim", description="Claim a friend code that was sent by a friend. Confused? "
                                                           "/friend-code-help")
    async def claim_code(self, ctx, code):
        code_json = "assets/bot/friend_code/codes.json"
        xp_json = "assets/bot/xp/xp.json"

        member = ctx.guild.get_member(ctx.author.id)
        joined_at = member.joined_at

        # Check if code exists
        with open(code_json, 'r') as f:
            data = json.load(f)

            for user, codes in data.items():
                if code in codes:
                    break
            else:
                await ctx.respond("That code doesn't exist. Check with the person you received it from.",
                                  ephemeral=True)
                return

        with open("assets/bot/friend_code/claimed.json", 'r') as f:
            claimed_users = json.load(f)

        # Check if user claimed a code already
        if str(user) in claimed_users:
            await ctx.respond("You already claimed a code!")
            return


        # User took too long to claim code
        if (datetime.datetime.now(pytz.UTC) - joined_at).total_seconds() > Constants.MAX_CLAIM_TIME:
            await ctx.respond(f"You took too long to claim the code. There is a maximum of {Constants.MAX_CLAIM_TIME}"
                              f" seconds to claim after joining.", ephemeral=True)

            with open(code_json, 'r+') as f:
                data = json.load(f)

                for user, codes in data.items():
                    if code in codes:
                        # Delete the now invalid code
                        data[user].remove(code)
                        break

                f.seek(0)
                json.dump(data, f)
                f.truncate()

            # Add user to list of people who claimed
            with open("assets/bot/friend_code/claimed.json", 'r+') as f:
                data = json.load(f)
                data.append(str(user))

                f.seek(0)
                json.dump(data, f)
                f.truncate()

            return

        with open(code_json, 'r') as f:
            data = json.load(f)

            for user, codes in data.items():
                if code in codes:
                    break

            # user who sent the friend code
            original_user_id = user
            original_user = await self.client.fetch_user(original_user_id)

            # Add inviter and claimer to inviters.json
            with open("assets/bot/friend_code/inviters.json", 'r+') as f:
                data = json.load(f)

                if not original_user_id in data:
                    data[original_user_id] = [str(ctx.author.id)]
                else:
                    data[original_user_id].append(str(ctx.author.id))

                f.seek(0)
                json.dump(data, f)
                f.truncate()

        with open(xp_json, 'r+') as f:
            data = json.load(f)

            if str(original_user_id) not in data:
                data[str(original_user_id)] = Constants.XPSettings.FRIEND_CODE_XP
            else:
                data[str(original_user_id)] += Constants.XPSettings.FRIEND_CODE_XP

            if str(ctx.author.id) not in data:
                data[str(original_user_id)] = Constants.XPSettings.FRIEND_CODE_CLAIMER_XP
            else:
                data[str(original_user_id)] += Constants.XPSettings.FRIEND_CODE_CLAIMER_XP

            f.seek(0)
            json.dump(data, f)
            f.truncate()

            await original_user.send(f"{ctx.author.mention} has claimed one of your friend codes. You have received "
                                     f"{Constants.XPSettings.FRIEND_CODE_XP} for inviting someone else to the server.")

        # Delete the code
        with open(code_json, 'r+') as f:
            data = json.load(f)
            data[user].remove(code)

            f.seek(0)
            json.dump(data, f)
            f.truncate()

        await ctx.respond(f"Code claimed! You got {Constants.XPSettings.FRIEND_CODE_CLAIMER_XP} XP.")

    @xp.command(name="query", description="Check how much XP you have.")
    async def xp_query(self, ctx, user: Option(discord.User, "User you want to check, defaults to you")=None):
        if not user:
            user = ctx.author

        xp_json = "assets/bot/xp/xp.json"

        with open(xp_json, 'r') as f:
            data = json.load(f)

        total_xp = 0

        if str(user.id) not in data:
            total_xp = 0

        else:
            total_xp = data[str(user.id)]

        await ctx.respond(f"{user.mention} has {total_xp} XP.")

    @commands.slash_command(name="subscribe", description="Get server announcements in your notifications.")
    async def subscribe(self, ctx):
        await ctx.author.add_roles(ctx.guild.get_role(1022599314402455612))
        await ctx.respond("Subscribed!")

    @commands.slash_command(name="unsubscribe", description="Stop getting server announcements")
    async def unsubscribe(self, ctx):
        await ctx.author.remove_roles(ctx.guild.get_role(1022599314402455612))
        await ctx.respond("Unsubscribed!")

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="error")
    async def error(self, ctx):
        raise Exception("This is an intentional error.")

    @commands.has_permissions(administrator=True)
    @xp.command(name="add", description="Add XP to a user")
    async def xp_add(self, ctx, user: Option(discord.User, "User you want to edit"), amount: Option(int, "Amount of XP to add")):
        utils.xp.add(user, amount)
        await ctx.respond("Added XP!", ephemeral=True)

    @commands.has_permissions(administrator=True)
    @xp.command(name="subtract", description="Subtract XP to a user")
    async def xp_subtract(self, ctx, user: Option(discord.User, "User you want to edit"),
                     amount: Option(int, "Amount of XP to subtract")):
        utils.xp.subtract(user, amount)
        await ctx.respond("Subtracted XP!", ephemeral=True)

    @commands.has_permissions(administrator=True)
    @xp.command(name="set", description="Set XP for a user")
    async def xp_set(self, ctx, user: Option(discord.User, "User you want to edit"),
                     amount: Option(int, "Amount of XP to add")):
        utils.xp.set_amount(user, amount)
        await ctx.respond("Set XP!", ephemeral=True)

    @xp.command(name="milestones", description="Check how much more XP to get to your next rank")
    async def xp_milestones(self, ctx, user: Option(discord.User, "User you want check, defaults to you")=None):
        if not user:
            user = ctx.author

        xp_amount = utils.xp.get_amount(user)
        em = discord.Embed(title="XP Milestones", description="Your road to victory", color=discord.Color.green())

        if not xp_amount >= Ranks.RANK_1:
            em.add_field(name="XP until Rank I", value=Ranks.RANK_1 - xp_amount, inline=False)

        if not xp_amount >= Ranks.RANK_2:
            em.add_field(name="XP until Rank II", value=Ranks.RANK_2 - xp_amount, inline=False)

        if not xp_amount >= Ranks.RANK_3:
            em.add_field(name="XP until Rank III", value=Ranks.RANK_3 - xp_amount, inline=False)

        if not xp_amount >= Ranks.RANK_4:
            em.add_field(name="XP until Rank IV", value=Ranks.RANK_4 - xp_amount, inline=False)

        if not xp_amount >= Ranks.RANK_5:
            em.add_field(name="XP until Rank V", value=Ranks.RANK_5 - xp_amount, inline=False)

        if xp_amount > Ranks.RANK_5:
            em.add_field(name="Damn..", value="You're at the top of the world! No more ranking up. "
                                              "You can still get more XP.")

        await ctx.respond(embed=em)
