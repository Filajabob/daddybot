from .item import Item

class ItemTicker:
    def __init__(self, item: Item, ticker_value: int, code: str):
        self.item = item
        self.ticker_value = ticker_value
        self.code = code


    def raw_data(self):
        return {
            "item": self.item,
            "ticker_value": self.ticker_value,
            "code": code
        }