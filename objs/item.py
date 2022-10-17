import discord
import utils

class Item:
    def __init__(self, id: str=None, name: str=None, cost: int=None, image_path: int=None, owner: discord.User=None):
        """
        Represents something that can be purchased in the Market
        """

        self.id = id
        self.name = name
        self.cost = cost
        self.image_path = image_path
        self.owner = owner

    def to_dict(self):
        return {
            "name": self.name,
            "cost": self.cost,
            "image_path": self.image_path,
            "owner": self.owner
        }

class XP(Item):
    """
    Represents 200 XP when bought in the Market
    """

    def default(owner):
        return XP(cost=utils.Constants.Market.XP_BUNDLE_COST, owner=owner)

