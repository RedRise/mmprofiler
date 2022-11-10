import logging
from models.order import TOLERANCE, Order, OrderType
from models.transaction import Transaction, take_maker_order
from models.offers_lists import OffersLists
from makers.maker import Maker
from typing import Callable


class MakerReplication(Maker):
    """This class implements a maket that deposits offers depending on a
    replication strategy i.e. delta_fun(x, t)."""

    offersLists: OffersLists

    # deltafun(price, time_to_live) -> delta
    maturity: float
    ttl: float
    deltaFun: Callable[[float, float], float]

    # (simplification pattern) this is like the mid_price that does not contains
    # offer. This price will be offered next time the best bid/ask is taken.
    currentMissingOffer: float
    lastOffer: float

    numOneWayOffers: int
    tickInterval: float
    tickQuantity: float

    @property
    def offers(self) -> OffersLists:
        return self.offersLists

    @property
    def midPrice(self):
        bid = self.offersLists.get_best_bid().price
        ask = self.offersLists.get_best_ask().price
        return (bid + ask) / 2

    def updateTime(self, time: float):
        """Update time, to update delta function"""
        self.ttl = max(0, self.maturity - time)

    def computeDelta(self, x: float) -> float:
        val = self.deltaFun(x, self.ttl)
        return val

    def _init_orderbook(self, initMidPrice: float, time: float):

        self.currentMissingOffer = None
        self.lastOffer = None
        self.offersLists.clear()

        delta_prev = self.asset  # self.computeDelta(initMidPrice)
        for i in range(1, self.numOneWayOffers + 1):
            price = initMidPrice - float(i) * self.tickInterval
            delta_current = self.computeDelta(price)
            gamma = delta_current - delta_prev
            delta_prev = delta_current
            # gamma should be positive because deltaFun should be decreasing
            if (price > 0) and (gamma > 0):
                self.offersLists.add_order(Order(OrderType.BUY, price, gamma))

        delta_prev = self.asset  # self.computeDelta(initMidPrice)
        for i in range(1, self.numOneWayOffers + 1):
            price = initMidPrice + float(i) * self.tickInterval
            delta_current = self.computeDelta(price)
            gamma = delta_current - delta_prev
            delta_prev = delta_current
            # gamma should be negatgive because deltaFun should be decreasing
            if gamma < 0:
                self.offersLists.add_order(Order(OrderType.SELL, price, -gamma))

    def __init__(
        self,
        initMidPrice: float,
        deltaFunction: Callable[[float, float], float],
        maturity: float,
        numOneWayOffers: int,
        tickInterval: float = None,
        tickQuantity: float = None,
    ):
        """
        initMidPrice    : first orderbook to setup
        deltaFunction   : (price, time_to_live) -> delta
        maturity        : maturity of the replication strategy
        numOneWayOffers : the number of offers to deposit on way (bids = asks)
        tickInterval    : if not None, offers will deployed every tickInterval x minTickSize
        tickQuantity    : if not None, offers will be deployed at prices that require delta adjustment of tickQuantity
        """
        super().__init__()
        self.deltaFun = deltaFunction
        self.maturity = maturity
        self.numOneWayOffers = numOneWayOffers
        self.tickInterval = tickInterval
        self.tickQuantity = tickQuantity
        self.offersLists = OffersLists()
        self.updateTime(0)
        self.swap_asset(self.computeDelta(initMidPrice), initMidPrice)
        self._init_orderbook(initMidPrice, 0)

    def buy_at_first_rank(self) -> Transaction:

        if not self.offersLists.has_ask():
            logging.error("No offer available, transaction failed.")
            return None

        best_ask = self.offersLists.pop_best_ask()

        self.cash += best_ask.quantity * best_ask.price
        self.asset -= best_ask.quantity

        # # replace liquidity
        # self.offersLists.ranked_bids.add(
        #     Order(OrderType.BUY, self.currentMissingOffer, best_ask.quantity)
        # )

        # update missing price offer
        self.currentMissingOffer = best_ask.price
        self.lastOffer = best_ask.price

        return take_maker_order(best_ask)

    def sell_at_first_rank(self) -> Transaction:

        if not self.offersLists.has_bid():
            logging.error("No bid available, transaction failed.")
            return None

        best_bid = self.offersLists.pop_best_bid()

        self.cash -= best_bid.quantity * best_bid.price
        self.asset += best_bid.quantity

        # # replace liquidity
        # self.offersLists.ranked_asks.add(
        #     Order(OrderType.SELL, self.currentMissingOffer, best_bid.quantity)
        # )

        # update missing price offer
        self.currentMissingOffer = best_bid.price
        self.lastOffer = best_bid.price

        return take_maker_order(best_bid)

    def post_hook(self, price: float, time: float):
        if self.lastOffer:
            self.updateTime(time)
            self._init_orderbook(price, time)
