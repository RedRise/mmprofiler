from models.order import Order, OrderType
import logging
from typing import List
from math import isclose


class OrderBook:
    tickSize = 0.01
    ranked_bids: List[Order] = []
    ranked_asks: List[Order] = []

    def __init__(self, tickSize: float) -> None:
        if tickSize <= 0:
            raise (ValueError("tickSize should be positive."))

        self.tickSize = tickSize
        self.ranked_bids = []
        self.ranked_asks = []

    def __str__(self) -> str:

        hline_template = "{:-^15}|{:-^15}||{:-^15}|{:-^15}\n"
        header_template = "{:^15}|{:^15}||{:^15}|{:^15}\n"
        info_template = "{:^15}|{:^15}||{:^15}|{:^15}\n"

        hline = hline_template.format("", "", "", "", fill="-")

        result = hline
        result += header_template.format("Qty Bid", "Px Bid", "Px Ask", "Qty Ask")
        result += hline

        for i in range(0, min([5, max(len(self.ranked_bids), len(self.ranked_asks))])):
            bid = self.ranked_bids[i] if len(self.ranked_bids) > i else None
            ask = self.ranked_asks[i] if len(self.ranked_asks) > i else None
            result += info_template.format(
                "{:.5f}".format(bid.quantity) if bid else "",
                "{:.5f}".format(bid.price) if bid else "",
                "{:.5f}".format(ask.price) if ask else "",
                "{:.5f}".format(ask.quantity) if ask else "",
            )

        return result

    def append_maker_order(self, order: Order):
        ticked_price = round(order.price / self.tickSize, 0) * self.tickSize
        if not isclose(order.price, ticked_price, rel_tol=1e-7):
            logging.error("Trying to push order with wrong tickSize.")
            return
        order.price = ticked_price

        if order.OrderType == OrderType.BUY:
            if self.has_bid():
                if self.ranked_bids[-1].price < order.price:
                    logging.error(
                        "can't append a bid at {0}, there is a worst bid".format(
                            order.price
                        )
                    )
                    raise Exception()

            self.ranked_bids.append(order)

        elif order.OrderType == OrderType.SELL:
            if self.has_ask():
                if order.price < self.ranked_asks[-1].price:
                    logging.error(
                        "can't append an ask at {0}, there is a worst ask".format(
                            order.price
                        )
                    )
                    raise Exception()

            self.ranked_asks.append(order)

        else:
            logging.info("Order type not recognized, nothing pushed.")

    def has_bid(self) -> bool:
        return len(self.ranked_bids) > 0

    def has_ask(self) -> bool:
        return len(self.ranked_asks) > 0

    def get_best_bid(self) -> Order:
        if self.has_bid():
            return self.ranked_bids[0]
        else:
            return None

    def get_best_ask(self) -> Order:
        if self.has_ask():
            return self.ranked_asks[0]
        else:
            return None

    def get_worst_bid(self) -> Order:
        if self.has_bid():
            return self.ranked_bids[-1]
        else:
            return None

    def get_worst_ask(self) -> Order:
        if self.has_ask():
            return self.ranked_asks[-1]
        else:
            return None

    def pop_best_bid(self) -> Order:
        return self.ranked_bids.pop(0)

    def pop_best_ask(self) -> Order:
        return self.ranked_asks.pop(0)
