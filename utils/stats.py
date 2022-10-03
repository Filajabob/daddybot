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
