import json
import discord
from .is_dev import is_dev
from .constants import Constants
from .errors import MissingFunds, InvalidMemeCoinBalance

def add_memecoin(user: discord.User, amount: int, client: discord.ext.commands.Bot, *, ignore_missing_funds=False):
    if not is_dev(client):
        path = "assets/bot/memecoin/memecoin.json"
    else:
        path = "assets/dev_bot/memecoin/memecoin.json"


    with open(path, 'r+') as f:
        data = json.load(f)

        if not str(user.id) in data:
            data[str(user.id)] = amount
        else:
            data[str(user.id)] += amount

        if (data[str(user.id)] + amount < 0) and not ignore_missing_funds:
            raise MissingFunds(f"{user.mention} does not have enough MemeCoin.")

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def subtract_memecoin(user: discord.User, amount: int, client: discord.ext.commands.Bot, *, ignore_missing_funds=False):
    add_memecoin(user, -amount, client, ignore_missing_funds=ignore_missing_funds)

def set_memecoin(user: discord.User, amount: int, client: discord.ext.commands.Bot):
    if amount < 0:
        raise InvalidMemeCoinBalance("Cannot set a user's balance to a negative number.")

    if not is_dev(client):
        path = "assets/bot/memecoin/memecoin.json"
    else:
        path = "assets/dev_bot/memecoin/memecoin.json"


    with open(path, 'r+') as f:
        data = json.load(f)
        data[str(user.id)] = amount

        f.seek(0)
        json.dump(data, f)
        f.truncate()

def get_memecoin(user, client):
    user = user.id

    if not is_dev(client):
        path = "assets/bot/memecoin/memecoin.json"
    else:
        path = "assets/dev_bot/memecoin/memecoin.json"

    with open(path, 'r') as f:
        data = json.load(f)

    if str(user) not in data:
        return 0
    else:
        return data[str(user)]


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
