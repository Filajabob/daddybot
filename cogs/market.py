import datetime

import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

import utils

class MarketCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    memecoin = SlashCommandGroup("memecoin", "Interact with the MemeCoin network")

    @memecoin.command(name="transfer", description="Transfer MemeCoin to someone")
    async def memecoin_transfer(self, ctx, recipent: Option(discord.User, "User to transfer to"),
                              amount: Option(int, "Amount of MemeCoin to transfer")):
        try:
            tax = utils.transfer_memecoin(ctx.author, recipent, amount, self.client)
        except utils.errors.MissingFunds:
            await ctx.respond("Too poor for that. That sucks lol")
            return

        await ctx.respond(f"Transferred MemeCoin. {tax} MemeCoin was taken for tax.")
        await recipent.send(f"You were just transferred {amount - tax} MemeCoin from {ctx.author.mention}")

    @memecoin.command(name="balance", description="Check your MemeCoin balance")
    async def memecoin_balance(self, ctx):
        amount = utils.get_memecoin(ctx.author, self.client)

        em = discord.Embed(title="Your Balance",
                           description="Your MemeCoin information brought to you by Meme Bank Inc.",
                           timestamp=datetime.datetime.now())
        em.add_field(name="Total MemeCoins", value=amount, inline=False)

        await ctx.respond(embed=em, ephemeral=True)

    @commands.has_permissions(administrator=True)
    @memecoin.command(name="add", description="Add MemeCoins to a user")
    async def memecoin_add(self, ctx, user: Option(discord.User, "User you want to edit"),
                     amount: Option(int, "Amount of XP to add")):
        utils.add_memecoin(user, amount, self.client)
        await ctx.respond("Added MemeCoin!", ephemeral=True)

    @commands.has_permissions(administrator=True)
    @memecoin.command(name="subtract", description="Subtract MemeCoins from a user")
    async def memecoin_subtract(self, ctx, user: Option(discord.User, "User you want to edit"),
                          amount: Option(int, "Amount of XP to subtract")):
        utils.subtract_memecoin(user, amount, self.client)
        await ctx.respond("Subtracted MemeCoin!", ephemeral=True)

    @commands.has_permissions(administrator=True)
    @memecoin.command(name="set", description="Set MemeCoins for a user")
    async def memecoin_set(self, ctx, user: Option(discord.User, "User you want to edit"),
                     amount: Option(int, "Amount of XP to add")):
        utils.set_memecoin(user, amount, self.client)
        await ctx.respond("Set MemeCoin!", ephemeral=True)