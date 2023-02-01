import json
import utils
from .item_ticker import ItemTicker
from .market_user import MarketUser

class Market:
    def __init__(self, client, tickers: list[ItemTicker], registered_users=list[MarketUser]):
        self.client = client
        self.dev = utils.is_dev(client)
        self.tickers = tickers
        self.registered_users = registered_users


    @staticmethod
    def restore_from_json(filepath):
        with open(filepath, 'r') as f:
            market_json = json.load(f)


    def save_to_json(self, filepath):
        data = {
            "client_id": self.client.id,
            "dev": self.dev,
            "tickers": [ticker.raw_data() for ticker in self.tickers]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f)


