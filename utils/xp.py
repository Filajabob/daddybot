import json

def add(user, amount):
    user = user.id

    with open("assets/bot/xp/xp.json", 'r+') as f:
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

def subtract(user, amount):
    return add(user, -amount)

def set_amount(user, amount):
    user = user.id

    with open("assets/bot/xp/xp.json", 'r+') as f:
        data = json.load(f)

        before = data[str(user)]
        data[str(user)] = amount

        f.seek(0)
        json.dump(data, f)
        f.truncate()

    return before