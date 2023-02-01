import datetime

import discord
from discord.ext import commands
from discord.commands import Option

import utils


class ModerationCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_permissions(ban_members=True)
    @commands.slash_command(name="ban", description="Ban a member from the server. Mods only.")
    async def ban(self, ctx, member: Option(discord.Member, "User to ban"),
                  incognito: Option(bool, "Should we tell this member who banned them?")=False,
                  reason: Option(str, "Why are you banning this user?")=None,
                  purge: Option(int, "How many days of messages to delete.", min_value=0, max_value=7)=0):

        em = discord.Embed(title="You were banned from Memetopia",
                           description="You read that properly, you were banned.")
        em.add_field(name="Oof..",
                     value="After consideration by the mods, you have been banned from Memetopia. Don't cry.",
                     inline=False)
        em.add_field(name="Reason", value=reason, inline=False)

        if incognito:
            em.add_field(name="Moderator", value="The moderator that banned you wishes to remain anonymous.",
                         inline=False)
        else:
            em.add_field(name="Moderator", value=f"You were banned by {ctx.author.mention}", inline=False)

        em.add_field(name="Farewell..", value="Whatever you did, hope you have a good life. You can appeal here: "
                                              "https://forms.gle/qSco7gWpcqhFsPYKA. Adios amigo!")

        await member.send(embed=em)
        await member.ban(delete_message_days=purge, reason=reason)

        await ctx.respond(f"{member.mention} has been banned. Reason: {reason}", ephemeral=True)

    @commands.has_permissions(kick_members=True)
    @commands.slash_command(name="kick", description="Kick a member from the server. Mods only.")
    async def kick(self, ctx, member: Option(discord.Member, "User to kick"),
                  incognito: Option(bool, "Should we tell this member who kicked them?") = False,
                  reason: Option(str, "Why are you kicking this user?") = None):

        em = discord.Embed(title="You were kicked from Memetopia",
                           description="You were just kicked from Memetopia.")
        em.add_field(name="Oof..",
                     value="After consideration by the mods, you have been kicked from Memetopia. Don't cry.",
                     inline=False)
        em.add_field(name="Reason", value=reason, inline=False)

        if incognito:
            em.add_field(name="Moderator", value="The moderator that kicked you wishes to remain anonymous.",
                         inline=False)
        else:
            em.add_field(name="Moderator", value=f"You were kicked by {ctx.author.mention}", inline=False)

        em.add_field(name="Come back?", value=f"If you wish to return, you can do so by clicking: "
                                              f"<{utils.Constants.INVITE_LINK}>")

        await member.send(embed=em)
        await member.kick(reason=reason)

        await ctx.respond(f"{member.mention} has been kicked.", ephemeral=True)

    @commands.has_permissions(moderate_members=True)
    @commands.slash_command(name="timeout", description="Give someone a timeout.")
    async def timeout(self, ctx,
                      member: Option(discord.Member, "User to timeout"),
                      reason: Option(str, "Reason for timeout")="No reason provided.",
                      duration: Option(str, "Amount of time to timeout.", choices=["60 Secs", "5 Mins", "10 Mins",
                                                                                   "1 Hour", "1 Day", "1 Week"])=None,
                      seconds: Option(int, "Amount of secs to timeout.")=None):
        if duration and seconds:
            await ctx.respond("Must provide duration OR seconds, not both", ephemeral=True)
            return

        if not (duration, seconds):
            await ctx.respond("Must provide duration OR seconds, not none", ephemeral=True)
            return

        em = discord.Embed(title="You were given a timeout in Memetopia", description="You were just given a timeout in "
                                                                                      "the Memetopia server.")
        em.add_field(name="Oof..",
                     value="After consideration by the mods, you have been given a timeout in Memetopia. Don't cry. "
                           "You can appeal here: https://forms.gle/qSco7gWpcqhFsPYKA",
                     inline=False)
        em.add_field(name="Reason", value=reason, inline=False)

        if duration:
            em.add_field(name="Time Until Released", value=duration)

            if duration == "60 Secs":
                duration = datetime.timedelta(seconds=60)
            elif duration == "5 Mins":
                duration = datetime.timedelta(minutes=5)
            elif duration == "10 Mins":
                duration = datetime.timedelta(minutes=10)
            elif duration == "1 Hour":
                duration = datetime.timedelta(hours=1)
            elif duration == "1 Day":
                duration = datetime.timedelta(days=1)
            elif duration == "1 Week":
                duration = datetime.timedelta(weeks=1)

        else:
            em.add_field(name="Time Until Released", value=f"{seconds} Seconds")

            duration = datetime.timedelta(seconds=seconds)

        await ctx.respond(f"{member.mention} has been timed out.", ephemeral=True)

        await member.send(embed=em)
        await member.timeout_for(duration, reason=reason)

    @commands.has_permissions(moderate_members=True)
    @commands.slash_command(name="remove-timeout", description="Remove a timeout from someone.")
    async def remove_timeout(self, ctx,
                             member: Option(discord.Member, "Member to remove timeout from"),
                             reason: Option(str, "Reason for timeout removal")):
        em = discord.Embed(title="You were released from timeout!",
                           description="You were released from a timeout in Memetopia!")
        em.add_field(name="You're lucky!",
                     value="After consideration by the mods, you were released from your timeout.",
                     inline=False)
        em.add_field(name="Reason", value=reason, inline=False)

        await ctx.respond(f"{member.mention} has been released.", ephemeral=True)

        await member.send(embed=em)
        await member.remove_timeout(reason=reason)

    @commands.has_permissions(manage_guild=True)
    @commands.slash_command(name="file", description="View the files in the bot. Admins only.")
    async def file(self, ctx, filepath):
        try:
            file = discord.File(filepath)
        except FileNotFoundError:
            await ctx.respond("File was not found.", ephemeral=True)
            return

        await ctx.respond(f"Requested file **{filepath}** was found", file=file)


