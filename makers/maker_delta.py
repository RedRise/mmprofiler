from cmath import isclose
import logging
from models.order import TOLERANCE, Order, OrderType
from models.transaction import Transaction, take_maker_order
from models.offers_lists import OffersLists
from makers.maker import Maker
from typing import Callable


def _round_tick_size(val: float, tick: float) -> float:
    return round(val / tick, 0) * tick


class MakerDelta(Maker):
    """This class implements a maket that deposits offers depending on a
    mm-delta function."""

    offersLists: OffersLists

    deltaFun: Callable[[float], float]

    currentMissingOffer: float

    # @property
    # def tickSize(self):
    #     return self.offersLists.tickSize

    @property
    def midPrice(self):
        bid = self.offersLists.get_best_bid().price
        ask = self.offersLists.get_best_ask().price
        return (bid + ask) / 2

    def _init_orderbook(self,
                        initMidPrice: float,
                        minTickSize: float,
                        numOneWayOffers: int,
                        tickInterval: int = None,
                        tickQuantity: float = None):

        self.currentMissingOffer = initMidPrice
        self.offersLists = OffersLists()

        delta_prev = self.deltaFun(initMidPrice)
        for i in range(1, numOneWayOffers + 1):
            price = initMidPrice - i * minTickSize * tickInterval
            delta_current = self.deltaFun(price)
            gamma = delta_current - delta_prev
            delta_prev = delta_current
            # gamma should be positive because deltaFun should be decreasing
            if (price > 0) and (gamma > 0):
                self.offersLists.add_maker_order(
                    Order(OrderType.BUY, price, gamma)
                )

        delta_prev = self.deltaFun(initMidPrice)
        for i in range(1, numOneWayOffers + 1):
            price = initMidPrice + i * minTickSize * tickInterval
            delta_current = self.deltaFun(price)
            gamma = delta_current - delta_prev
            delta_prev = delta_current
            # gamma should be negatgive because deltaFun should be decreasing
            if (gamma < 0):
                self.offersLists.add_maker_order(
                    Order(OrderType.SELL, price, - gamma))

    def __init__(
        self,
        initMidPrice: float,
        deltaFunction: Callable[[float], float],
        minTickSize: float,
        numOneWayOffers: int,
        tickInterval: int = None,
        tickQuantity: float = None
    ):
        """
        minTickSize     : the tickSize of the underlying internal orderBook
        numOneWayOffers : the number of offers to deposit on way (bids = asks)
        tickInterval    : if not None, offers will deployed every tickInterval x minTickSize
        tickQuantity    : if not None, offers will be deployed at prices that require delta adjustment of tickQuantity
        """
        super().__init__()
        self.deltaFun = deltaFunction
        self._init_orderbook(
            initMidPrice, minTickSize, numOneWayOffers, tickInterval, tickQuantity)

    def start_trading_session(self):
        pass

    def buy_at_first_rank(self) -> Transaction:

        if not self.offersLists.has_ask():
            logging.error("No offer available, transaction failed.")
            return None

        best_ask = self.offersLists.pop_best_ask()

        self.cash += best_ask.quantity * best_ask.price
        self.asset -= best_ask.quantity

        # replace liquidity
        self.offersLists.ranked_bids.add(
            Order(OrderType.BUY, self.currentMissingOffer, best_ask.quantity))

        # update missing price offer
        self.currentMissingOffer = best_ask.price

        return take_maker_order(best_ask)

    def sell_at_first_rank(self) -> Transaction:

        if not self.offersLists.has_bid():
            logging.error("No bid available, transaction failed.")
            return None

        best_bid = self.offersLists.pop_best_bid()

        self.cash -= best_bid.quantity * best_bid.price
        self.asset += best_bid.quantity

        # replace liquidity
        self.offersLists.ranked_asks.add(
            Order(OrderType.SELL, self.currentMissingOffer, best_bid.quantity))

        # update missing price offer
        self.currentMissingOffer = best_bid.price

        return take_maker_order(best_bid)
