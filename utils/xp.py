import json
import objs
from .is_dev import is_dev
from .constants import Constants

def add(user, amount, dev):
    user = user.id

    if not dev:
        path = "assets/bot/xp/xp.json"
    else:
        path = "assets/dev_bot/xp/xp.json"

    with open(path, 'r+') as f:
        data = json.load(f)

        if str(user) not in data:
            before = 0
            data[str(user)] = amount
            after = amount
        else:
            before = data[str(user)]
            data[str(user)] += amount
            after = data[str(user)] + amount

        f.seek(0)
        json.dump(data, f)
        f.truncate()

    return before, after

def subtract(user, amount, dev):
    return add(user, -amount, dev)

def set_amount(user, amount, dev):
    user = user.id

    if not dev:
        path = "assets/bot/xp/xp.json"
    else:
        path = "assets/dev_bot/xp/xp.json"

    with open(path, 'r+') as f:
        data = json.load(f)

        if str(user) in data:
            before = data[str(user)]
        else:
            before = 0

        data[str(user)] = amount

        f.seek(0)
        json.dump(data, f)
        f.truncate()

    return before

def get_amount(user, dev):
    user = user.id

    if not dev:
        path = "assets/bot/xp/xp.json"
    else:
        path = "assets/dev_bot/xp/xp.json"

    with open(path, 'r') as f:
        data = json.load(f)

    if str(user) not in data:
        return 0
    else:
        return data[str(user)]

def add_xp_from_market(xp_item: objs.XP, client):
    return add(xp_item.owner, Constants.Market.XP_BUNDLE_SIZE, is_dev(client))
