from .item import Item

class MarketUser:
    def __init__(self, discord_id: int, owned_items: list[Item]):
        self.discord_id = discord_id
