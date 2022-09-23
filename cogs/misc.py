import json
import random
import string
import datetime
import pytz

import discord
from discord.ext import commands

# TODO: Move constants.py
from .constants import Constants


class MiscCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name="ping", description="Get the bot's latency")
    async def ping(self, ctx):
        """Get the bot's latency"""
        await ctx.respond(f"Pong! Latency: {round(self.client.latency, 2)}ms")

    @commands.slash_command(name="reset-codes", description="Reset all your codes. No going back!")
    async def reset_codes(self, ctx):
        await ctx.respond("Friend codes are in progress")
        return

        code_json = "assets/bot/friend_code/codes.json"

        with open(code_json, 'r+') as f:
            data = json.load(f)
            data[str(ctx.author.id)] = []

            f.seek(0)
            json.dump(data, f)
            f.truncate()

        await ctx.respond("Codes have been reset.", ephemeral=True)

    @commands.slash_command(name="friend-code", description="Generate a code that you can send to a friend when you "
                                                            "invite them. Gets you and them XP.")
    async def friend_code(self, ctx):
        await ctx.respond("Friend codes are in progress")
        return

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

        await ctx.respond(f"Your friend code has been created. Keep it safe! Code: **{code}**", ephemeral=True)

    @commands.slash_command(name="claim-code", description="Claim a friend code that was sent by a friend")
    async def claim_code(self, ctx, code):
        await ctx.respond("Friend codes are in progress")
        return

        code_json = "assets/bot/friend_code/codes.json"
        member = ctx.guild.get_member(ctx.author.id)
        joined_at = member.joined_at

        # Check if code exists
        with open(code_json, 'r') as f:
            data = json.load(f)

            for user, codes in data.items():
                if code in codes:
                    break
            else:
                await ctx.respond("That code doesn't exist. Check with the person you recieved it from.",
                                  ephemeral=True)
                return

        with open("assets/bot/friend_code/claimed.json", 'r') as f:
            claimed_users = json.load(f)

        # Check if user claimed a code already
        if str(user.id) in claimed_users:
            await ctx.respond("You already claimed a code!")
            return


        # User took too long to claim code
        if (datetime.datetime.now(pytz.UTC) - joined_at).total_seconds() > Constants.MAX_CLAIM_TIME:
            await ctx.respond(f"You took too long to claim the code. There is a maximum of {Constants.MAX_CLAIM_TIME}"
                              f" seconds to claim.", ephemeral=True)

            with open(code_json, 'r') as f:
                data = json.load(f)

                for user, codes in data.items():
                    if code in codes:
                        # Delete the now invalid code
                        del data[user][data[user][code].index()]
                        break

                f.seek(0)
                json.dump(data, f)
                f.truncate()

            # Add user to list of people who claimed
            with open("assets/bot/friend_code/claimed.json", 'r+') as f:
                data = json.load(f)
                data.append(str(user.id))

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
            original_user = user

            # TODO: Continue from here


        # Delete the code
        with open(code_json, 'r+') as f:
            data = json.load(f)
            del data[user][data[user][code].index()]

            f.seek(0)
            json.dump(data, f)
            f.truncate()
