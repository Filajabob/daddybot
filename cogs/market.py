import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

import utils

class MarketCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    market = SlashCommandGroup("market", "Interact with the Market")

    @market.command(name="transfer", description="Transfer MemeCoin to someone")
    async def market_transfer(self, ctx, recipent: Option(discord.User, "User to transfer to"),
                              amount: Option(int, "Amount of MemeCoin to transfer")):
        try:
            tax = utils.transfer_memecoin(ctx.author, recipent, amount, self.client)
        except utils.errors.MissingFunds:
            await ctx.respond("Too poor for that. That sucks lol")
            return

        await ctx.respond(f"Transferred MemeCoin. {tax} MemeCoin was taken for tax.")