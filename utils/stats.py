import os
import datetime
from .is_dev import is_dev

def log_msg(msg, client):
    dev = is_dev(client)

    if not dev:
        parent_dir = "assets/bot/stats/message_stats"
    else:
        parent_dir = "assets/dev_bot/stats/message_stats"

    today = datetime.date.today()
    parent_dir = os.path.join(parent_dir, str(today.year), str(today.month), str(today.day))
    path = os.path.join(parent_dir, "msgs.txt")

    os.makedirs(parent_dir, exist_ok=True)

    if not os.path.isfile(path):
        with open(path, 'w') as f:
            f.write("0")

    with open(path, 'r+') as f:
        previous = int(f.read())
        f.seek(0)
        f.write(str(previous + 1))

def get_msg_stats(client, date=None):
    if not date:
        date = datetime.date.today()

    dev = is_dev(client)

    if not dev:
        parent_dir = "assets/bot/stats/message_stats"
    else:
        parent_dir = "assets/dev_bot/stats/message_stats"

    parent_dir = os.path.join(parent_dir, str(date.year), str(date.month), str(date.day))
    path = os.path.join(parent_dir, "msgs.txt")

    if not os.path.isfile(path):
        return 0

    with open(path, 'r') as f:
        return int(f.read())

def log_member_join(member, client):
    dev = is_dev(client)

    if not dev:
        parent_dir = "assets/bot/stats/member_join_stats"
    else:
        parent_dir = "assets/dev_bot/stats/member_join_stats"

    today = datetime.date.today()
    parent_dir = os.path.join(parent_dir, str(today.year), str(today.month), str(today.day))
    path = os.path.join(parent_dir, "joins.txt")

    os.makedirs(parent_dir, exist_ok=True)

    if not os.path.isfile(path):
        with open(path, 'w') as f:
            f.write("0")

    with open(path, 'r+') as f:
        previous = int(f.read())
        f.seek(0)
        f.write(str(previous + 1))

def get_member_join_stats(client, date=None):
    if not date:
        date = datetime.date.today()

    dev = is_dev(client)

    if not dev:
        parent_dir = "assets/bot/stats/member_join_stats"
    else:
        parent_dir = "assets/dev_bot/stats/member_join_stats"

    parent_dir = os.path.join(parent_dir, str(date.year), str(date.month), str(date.day))
    path = os.path.join(parent_dir, "joins.txt")

    if not os.path.isfile(path):
        return 0

    with open(path, 'r') as f:
        return int(f.read())

def log_member_leave(member, client):
    dev = is_dev(client)

    if not dev:
        parent_dir = "assets/bot/stats/member_leave_stats"
    else:
        parent_dir = "assets/dev_bot/stats/member_leave_stats"

    today = datetime.date.today()
    parent_dir = os.path.join(parent_dir, str(today.year), str(today.month), str(today.day))
    path = os.path.join(parent_dir, "leaves.txt")

    os.makedirs(parent_dir, exist_ok=True)

    if not os.path.isfile(path):
        with open(path, 'w') as f:
            f.write("0")

    with open(path, 'r+') as f:
        previous = int(f.read())
        f.seek(0)
        f.write(str(previous + 1))

def get_member_leave_stats(client, date=None):
    if not date:
        date = datetime.date.today()

    dev = is_dev(client)

    if not dev:
        parent_dir = "assets/bot/stats/member_leave_stats"
    else:
        parent_dir = "assets/dev_bot/stats/member_leave_stats"

    parent_dir = os.path.join(parent_dir, str(date.year), str(date.month), str(date.day))
    path = os.path.join(parent_dir, "leaves.txt")

    if not os.path.isfile(path):
        return 0

    with open(path, 'r') as f:
        return int(f.read())

def log_vc_seconds(client, seconds=10):
    dev = is_dev(client)

    if not dev:
        parent_dir = "assets/bot/stats/vc_stats"
    else:
        parent_dir = "assets/dev_bot/stats/vc_stats"

    today = datetime.date.today()
    parent_dir = os.path.join(parent_dir, str(today.year), str(today.month), str(today.day))

    path = os.path.join(parent_dir, "seconds.txt")

    if not os.path.isfile(path):
        os.makedirs(parent_dir, exist_ok=True)
        with open(path, 'w') as f:
            f.write("0")

    with open(path, 'r+') as f:
        prev = int(f.read())
        after = prev + seconds

        f.seek(0)
        f.write(str(after))

def get_vc_seconds(client, date=None):
    if not date:
        date = datetime.date.today()

    dev = is_dev(client)

    if not dev:
        parent_dir = "assets/bot/stats/vc_stats"
    else:
        parent_dir = "assets/dev_bot/stats/vc_stats"

    today = datetime.date.today()

    parent_dir = os.path.join(parent_dir, str(date.year), str(date.month), str(date.day))
    path = os.path.join(parent_dir, "seconds.txt")

    if not os.path.isfile(path):
        return 0

    with open(path, 'r') as f:
        return int(f.read())
