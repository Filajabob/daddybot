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

        em.add_field(name="Farewell..", value="Whatever you did, hope you have a good life. Adios!")

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

