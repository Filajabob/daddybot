import json
import discord
from .is_dev import is_dev
from .constants import Constants
from .errors import MissingFunds

def add_memecoin(user: discord.User, amount: int, client: discord.ext.commands.Bot):
    if not is_dev(client):
        path = "assets/bot/memecoin/memecoin.json"
    else:
        path = "assets/dev_bot/memecoin/memecoin.json"


    with open(path, 'r+') as f:
        data = json.load(f)

        if data[str(user.id)] + amount < 0:
            raise MissingFunds(f"{user.mention} does not have enough MemeCoin.")

        if not str(user.id) in data:
            data[str(user.id)] = amount
        else:
            data[str(user.id)] += amount

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def subtract_memecoin(user: discord.User, amount: int, client: discord.ext.commands.Bot):
    add_memecoin(user, -amount, client)

def transfer_memecoin(sender: discord.User, recipent: discord.User, amount: int, client: discord.ext.commands.Bot, *,
             tax: float=Constants.MemeCoin.TAX_PERCENTAGE,
             tax_minimum: int=Constants.MemeCoin.TAX_MINIMUM):
    if amount >= tax_minimum:
        real_amount = amount - (amount * tax)
    else:
        real_amount = amount

    subtract_memecoin(sender, real_amount, client)
    add_memecoin(recipent, real_amount, client)

    return amount - real_amount
