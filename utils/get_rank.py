import discord
from .constants import Constants
from .is_dev import is_dev
from .xp import get_amount

def get_rank(user: discord.User, client: discord.ext.commands.Bot):
    """
    Get the rank of the user.

    Returns an int corresponding with their rank.
    0 is unranked, 1 is Rank 1, etc.
    """
    xp_amount = get_amount(user, is_dev(client))

    if xp_amount < Constants.Ranks.RANK_1:
        return 0
    elif xp_amount < Constants.Ranks.RANK_2:
        return 1
    elif xp_amount < Constants.Ranks.RANK_3:
        return 2
    elif xp_amount < Constants.Ranks.RANK_4:
        return 3
    elif xp_amount < Constants.Ranks.RANK_5:
        return 4
    else:
        return 5