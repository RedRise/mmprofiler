from cmath import isclose
import logging
from models.order import TOLERANCE, Order, OrderType
from models.transaction import Transaction, take_maker_order
from models.orderbook import OrderBook
from makers.maker import Maker


def _round_tick_size(val: float, tick: float) -> float:
    return round(val / tick, 0) * tick


class MakerZeroKnowledge(Maker):
    """This class implements the zero knownledge MM, deploying a strip of
    offers, every tickSize"""

    orderBook: OrderBook

    @property
    def tickSize(self):
        return self.orderBook.tickSize

    @property
    def midPrice(self):
        bid = self.orderBook.get_best_bid().price
        ask = self.orderBook.get_best_ask().price
        return (bid + ask) / 2

    def _init_orderbook(
        self,
        initMidPrice: float,
        tickSize: float,
        numBids: int,
        sizeBid: float,
        numAsks: int,
        sizeAsk: float,
    ):
        self.orderBook = OrderBook(tickSize)

        midPrice = _round_tick_size(initMidPrice, tickSize)

        for i in range(1, numBids + 1):
            price = midPrice - i * tickSize
            if price > 0:
                self.orderBook.append_maker_order(
                    Order(OrderType.BUY, price, sizeBid)
                )

        for i in range(1, numAsks + 1):
            price = midPrice + i * tickSize
            self.orderBook.append_maker_order(
                Order(OrderType.SELL, price, sizeAsk))

        self.orderBook.ranked_asks.sort(key=lambda x: x.price)
        self.orderBook.ranked_bids.sort(key=lambda x: x.price, reverse=True)

    def __init__(
        self,
        initMidPrice: float,
        tickSize: float,
        numBids: int,
        sizeBid: float,
        numOffers: int,
        sizeOffer: float,
    ):
        """
        initMidPrice : starting price to count ticks and deposit offers. No offer on this price.
        numBids      : the number of bids that will be deposited
        sizeBids     : the size of the bid offers
        numAsks      : the number of asks that will be deposited
        sizeAsk      : the size of the ask offers
        """
        super().__init__()
        self._init_orderbook(
            initMidPrice, tickSize, numBids, sizeBid, numOffers, sizeOffer
        )

    def start_trading_session(self):
        pass

    def buy_at_first_rank(self) -> Transaction:

        if not self.orderBook.has_ask():
            logging.error("No offer available, transaction failed.")
            return None

        best_offer = self.orderBook.pop_best_ask()

        tx = take_maker_order(best_offer)
        self.cash += best_offer.quantity * best_offer.price
        self.asset -= best_offer.quantity

        # replace liquidity
        new_price = best_offer.price - self.orderBook.tickSize
        incr_quantity = best_offer.quantity * best_offer.price / new_price

        best_bid = self.orderBook.get_best_bid()

        if best_bid and isclose(best_bid.price, new_price, rel_tol=TOLERANCE):
            best_bid.quantity += incr_quantity
        else:
            new_bid = Order(OrderType.BUY, new_price, incr_quantity)
            self.orderBook.ranked_bids.insert(0, new_bid)

        return tx

    def sell_at_first_rank(self) -> Transaction:

        if not self.orderBook.has_bid():
            logging.error("No bid available, transaction failed.")
            return None

        best_bid = self.orderBook.pop_best_bid()

        self.cash -= best_bid.quantity * best_bid.price
        self.asset += best_bid.quantity

        # replace liquidity
        new_price = best_bid.price + self.orderBook.tickSize
        incr_quantity = best_bid.quantity * best_bid.price / new_price

        best_offer = self.orderBook.get_best_ask()
        if best_offer and isclose(best_offer.price, new_price, rel_tol=TOLERANCE):
            best_offer.quantity += incr_quantity
        else:
            new_offer = Order(OrderType.SELL, new_price, incr_quantity)
            self.orderBook.ranked_asks.insert(0, new_offer)

        tx = take_maker_order(best_bid)

        return tx
