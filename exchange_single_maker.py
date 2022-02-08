from models.orderbook import OrderBook
from models.transaction import Transaction
from makers.single_maker_zero_knowledge import SingleMakerZeroKnowledge
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

    def __init__(self, maker: SingleMakerZeroKnowledge) -> None:
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

        offer = self.orderBook.get_best_offer()
        if offer and offer.price < price:
            _ = self.buy_at_first_rank()
            self.apply_arbitrage(price)
        else:
            bid = self.orderBook.get_best_bid()
            if bid and price <= bid.price:
                _ = self.sell_at_first_rank()
                self.apply_arbitrage(price)
