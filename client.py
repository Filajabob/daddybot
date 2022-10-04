import os
import logging

import discord
from discord.ext import commands

# Cogs
from cogs.events import EventCog
from cogs.misc import MiscCog
from cogs.fun import FunCog
from cogs.music import MusicCog
from cogs.tasks import TaskCog
from cogs.moderation import ModerationCog
from cogs.stats import StatsCog

__version__ = "0.1.0"

# Setup logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(name)s: %(message)s'))
logger.addHandler(handler)

# Constants
TOKEN_PATH = "assets/auth/TOKEN.txt"
DEV_TOKEN_PATH = "assets/auth/DEV_TOKEN.txt"

intents = discord.Intents.all()

client = commands.Bot(command_prefix="d!", debug_guilds=["1021919859203903488"], intents=intents)
client.remove_command("help")


# Add Cogs
client.add_cog(EventCog(client))
client.add_cog(MiscCog(client))
client.add_cog(FunCog(client))
client.add_cog(MusicCog(client))
client.add_cog(TaskCog(client))
client.add_cog(ModerationCog(client))
client.add_cog(StatsCog(client))

dev = input("Run the Developer bot? (y/N) ") == "y"

if not dev:
    with open(TOKEN_PATH) as f:
        TOKEN = f.read()
else:
    print("Running dev bot...")
    with open(DEV_TOKEN_PATH) as f:
        TOKEN = f.read()

client.run(TOKEN)
