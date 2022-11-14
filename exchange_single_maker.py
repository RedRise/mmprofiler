from cmath import isclose
from models.order import TOLERANCE
from models.offers_lists import OffersLists
from models.transaction import Transaction
from makers.maker import Maker
from typing import List

# first implementation of single-maker/single-taker exchange


class ExchangeSingleMaker:

    transactions: List[Transaction] = []
    time: float

    @property
    def offers(self) -> OffersLists:
        return self.maker.offers

    @property
    def midPrice(self) -> float:
        return self.offers.midPrice

    def __init__(self, maker: Maker) -> None:
        self.transactions = []
        self.maker = maker
        self.time = 0

    def buy_at_first_rank(self) -> Transaction:
        transaction = self.maker.buy_at_first_rank()
        if transaction:
            transaction.time = self.time
            self.transactions.append(transaction)
        return transaction

    def sell_at_first_rank(self) -> Transaction:
        transaction = self.maker.sell_at_first_rank()
        if transaction:
            transaction.time = self.time
            self.transactions.append(transaction)
        return transaction

    def _take_to_price(self, price: float):
        """logic of external price coming to arbitrage the exchange. Maker
        orders are taken until price fit in bid/offer.
        Warning on matching price with maker order limit (we dont trade the
        liquidity redeployed, infinite loop if redeployed at same price).
        """
        offer = self.offers.get_best_ask()
        if offer and offer.price <= price:
            _ = self.buy_at_first_rank()
            if offer and not isclose(offer.price, price, rel_tol=TOLERANCE):
                self._take_to_price(price)
        else:
            bid = self.offers.get_best_bid()
            if bid and price <= bid.price:
                _ = self.sell_at_first_rank()
                if bid and not isclose(bid.price, price, rel_tol=TOLERANCE):
                    self._take_to_price(price)

    def apply_arbitrage(self, price: float, time: float = None):
        """logic of external price coming to arbitrage the exchange. Maker
        orders are taken until price fit in bid/offer.
        Warning on matching price with maker order limit (we dont trade the
        liquidity redeployed, infinite loop if redeployed at same price).
        """
        self.time = time

        self._take_to_price(price)

        self.maker.post_hook(price, time)
