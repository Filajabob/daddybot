class MissingFunds(Exception):
    pass

class InvalidMemeCoinBalance(Exception):
    pass

class FeatureNotImplemented(Exception):
    def __init__(self, message="This feature has not been implemented yet."):
        self.message = message
        super().__init__(self.message)