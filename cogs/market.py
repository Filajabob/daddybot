import datetime
import json

import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from discord.ui import View

import utils
from utils import Constants
import objs

class MarketCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    memecoin = SlashCommandGroup("memecoin", "Interact with the MemeCoin network")
    market = SlashCommandGroup("market", "Interact with the Meme Market")

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

    @market.command(name="shop", description="Check out the generic item shop")
    async def market_shop(self, ctx):
        client = self.client

        with open("assets/bot/market/items/generic.json", 'r') as f:
            items = json.load(f)

        options = []
        for id, item in items.items():
            options.append(
                discord.SelectOption(
                    label=f"{item['name']} ({item['cost']} MC)",
                    description=item["description"],
                    value=id
                )
            )

        class ShopView(View):
            @discord.ui.select(
                placeholder="Pick an item to buy",
                min_values=0,
                max_values=1,
                options=options,
            )
            async def select_callback(self, select, inter):
                if select.values[0] == "xp":
                    xp_bundle = objs.XP.default(ctx.author)
                    utils.subtract_memecoin(ctx.author, Constants.Market.XP_BUNDLE_COST, client)
                    utils.xp.add_xp_from_market(xp_bundle, client)

                else:
                    # for future items
                    pass

                self.disable_all_items()
                await inter.response.send_message("Successfully purchased item!")


        await ctx.respond("Buy something from the menu:", view=ShopView())
