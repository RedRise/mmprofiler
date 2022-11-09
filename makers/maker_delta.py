from cmath import isclose
import logging
from models.order import TOLERANCE, Order
from models.transaction import Transaction, take_maker_order
from models.offers_lists import OffersLists
from makers.maker import Maker


def _round_tick_size(val: float, tick: float) -> float:
    return round(val / tick, 0) * tick


class MakerDelta(Maker):
    """This class implements a maket that deposits offers depending on a
    mm-delta function."""

    offersLists: OffersLists

    @property
    def tickSize(self):
        return self.offersLists.tickSize

    @property
    def midPrice(self):
        bid = self.offersLists.get_best_bid().price
        ask = self.offersLists.get_best_offer().price
        return (bid + ask) / 2

    def _init_orderbook(self, initMidPrice: float, delta_function, tick_spacer):
        """
        initMidPrice : starting price to count ticks and deposit offers. No offer on this price.
        """

        self.offersLists = OrderBook(tickSize)

        midPrice = _round_tick_size(initMidPrice, tickSize)

        for i in range(1, numBids + 1):
            price = midPrice - i * tickSize
            if price > 0:
                self.offersLists.push_maker_order(
                    Order(OrderType.BUY, price, sizeBid, 1)
                )

        for i in range(1, numAsks + 1):
            price = midPrice + i * tickSize
            self.offersLists.push_maker_order(Order(OrderType.SELL, price, sizeAsk, 1))

        self.offersLists.ranked_offers.sort(key=lambda x: x.price)
        self.offersLists.ranked_bids.sort(key=lambda x: x.price, reverse=True)

    def __init__(
        self,
        initMidPrice: float,
        deltaFunction,
        minTickSize: float,
        numOneWayOffers: int,
        tickInterval: int = None,
        tickQuantity: float = None,
    ):
        """
        minTickSize     : the tickSize of the underlying internal orderBook
        numOneWayOffers : the number of offers to deposit on way (bids = asks)
        tickInterval    : if not None, offers will deployed every tickInterval x minTickSize
        tickQuantity    : if not None, offers will be deployed at prices that require delta adjustment of tickQuantity
        """
        super().__init__()
        self._init_orderbook(
            initMidPrice, tickSize, numBids, sizeBid, numOffers, sizeOffer
        )

    def start_trading_session(self):
        pass

    def buy_at_first_rank(self) -> Transaction:

        if not self.offersLists.has_offer():
            logging.error("No offer available, transaction failed.")
            return None

        best_offer = self.offersLists.pop_best_offer()

        tx = take_maker_order(best_offer)
        self.cash += best_offer.quantity * best_offer.price
        self.asset -= best_offer.quantity

        # replace liquidity
        new_price = best_offer.price - self.offersLists.tickSize
        incr_quantity = best_offer.quantity * best_offer.price / new_price

        best_bid = self.offersLists.get_best_bid()

        if best_bid and isclose(best_bid.price, new_price, rel_tol=TOLERANCE):
            best_bid.quantity += incr_quantity
        else:
            new_bid = Order(OrderType.BUY, new_price, incr_quantity, 0)
            self.offersLists.ranked_bids.insert(0, new_bid)

        return tx

    def sell_at_first_rank(self) -> Transaction:

        if not self.offersLists.has_bid():
            logging.error("No bid available, transaction failed.")
            return None

        best_bid = self.offersLists.pop_best_bid()

        self.cash -= best_bid.quantity * best_bid.price
        self.asset += best_bid.quantity

        # replace liquidity
        new_price = best_bid.price + self.offersLists.tickSize
        incr_quantity = best_bid.quantity * best_bid.price / new_price

        best_offer = self.offersLists.get_best_offer()
        if best_offer and isclose(best_offer.price, new_price, rel_tol=TOLERANCE):
            best_offer.quantity += incr_quantity
        else:
            new_offer = Order(OrderType.SELL, new_price, incr_quantity, 0)
            self.offersLists.ranked_offers.insert(0, new_offer)

        tx = take_maker_order(best_bid)

        return tx
