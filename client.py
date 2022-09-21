import os
import logging

import discord
from discord.ext import commands

# Cogs
from cogs.events import EventCog
from cogs.misc import MiscCog

# Setup logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(name)s: %(message)s'))
logger.addHandler(handler)

# Constants
TOKEN_PATH = "assets/auth/TOKEN.txt"
DEV_TOKEN_PATH = "assets/auth/DEV_TOKEN.txt"
client = commands.Bot(debug_guilds=["813594607324758066", "1021919859203903488"])

# Check if TOKEN.txt exists
if not (os.path.exists(TOKEN_PATH) or os.path.exists(DEV_TOKEN_PATH)):
    raise FileNotFoundError("TOKEN.txt or DEV_TOKEN.txt was not found. Make sure to add TOKEN.txt to the assets/auth directory.")

client.remove_command("help")

# Add Cogs
client.add_cog(EventCog(client))
client.add_cog(MiscCog(client))

dev = input("Run the Developer bot? (y/N) ") == "y"

if not dev:
    with open(TOKEN_PATH) as f:
        TOKEN = f.read()
else:
    print("Running dev bot...")
    with open(DEV_TOKEN_PATH) as f:
        TOKEN = f.read()


client.run(TOKEN)
