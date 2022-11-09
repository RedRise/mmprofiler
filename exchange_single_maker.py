from cmath import isclose
from models.order import TOLERANCE
from models.orderbook import OrderBook
from models.transaction import Transaction
from makers.maker_zero_knowledge import MakerZeroKnowledge
from typing import List

# first implementation of single-maker/single-taker exchange


class ExchangeSingleMaker():

    transactions: List[Transaction] = []

    @property
    def orderBook(self) -> OrderBook:
        return self.maker.orderBook

    @property
    def midPrice(self):
        return self.maker.midPrice

    def __init__(self, maker: MakerZeroKnowledge) -> None:
        self.transactions = []
        self.maker = maker

    def start_trading_session(self):
        self.maker.start_trading_session()

    def buy_at_first_rank(self) -> transactions:
        transaction = self.maker.buy_at_first_rank()
        if transaction:
            self.transactions.append(transaction)
        return transaction

    def sell_at_first_rank(self):
        transaction = self.maker.sell_at_first_rank()
        if transaction:
            self.transactions.append(transaction)
        return transaction

    def apply_arbitrage(self, price: float):    
        """ logic of external price coming to arbitrage the exchange. Maker 
        orders are taken until price fit in bid/offer.
        Warning on matching price with maker order limit (we dont trade the
        liquidity redeployed, infinite loop if redeployed at same price).
        """
        offer = self.orderBook.get_best_ask()
        if offer and offer.price <= price:
            _ = self.buy_at_first_rank()
            if offer and not isclose(offer.price, price, rel_tol=TOLERANCE):
                self.apply_arbitrage(price)
        else:
            bid = self.orderBook.get_best_bid()
            if bid and price <= bid.price:
                _ = self.sell_at_first_rank()
                if bid and not isclose(bid.price, price, rel_tol=TOLERANCE):
                    self.apply_arbitrage(price)
