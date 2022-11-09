from models.order import Order, OrderType
from sortedcontainers import SortedList
import logging
from typing import List
# from math import isclose


class OffersLists():

    ranked_bids: SortedList
    ranked_asks: SortedList

    def __init__(self) -> None:
        self.ranked_bids = SortedList()
        self.ranked_asks = SortedList()

    def __str__(self) -> str:

        hline_template = "{:-^15}|{:-^15}||{:-^15}|{:-^15}\n"
        header_template = "{:^15}|{:^15}||{:^15}|{:^15}\n"
        info_template = "{:^15}|{:^15}||{:^15}|{:^15}\n"

        hline = hline_template.format("", "", "", "", fill="-")

        result = hline
        result += header_template.format("Qty Bid",
                                         "Px Bid", "Px Ask", "Qty Ask")
        result += hline

        for i in range(0, min([5, max(len(self.ranked_bids), len(self.ranked_asks))])):
            bid = self.ranked_bids[i] if len(self.ranked_bids) > i else None
            ask = self.ranked_asks[i] if len(
                self.ranked_asks) > i else None
            result += info_template.format(
                "{:.5f}".format(bid.quantity) if bid else "",
                "{:.5f}".format(bid.price) if bid else "",
                "{:.5f}".format(ask.price) if ask else "",
                "{:.5f}".format(ask.quantity) if ask else ""
            )

        return result

    def add_maker_order(self, order: Order):

        if (order.order_type == OrderType.BUY):
            self.ranked_bids.add(order)
        elif (order.order_type == OrderType.SELL):
            self.ranked_asks.add(order)
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

    def pop_best_bid(self) -> Order:
        return self.ranked_bids.pop(0)

    def pop_best_ask(self) -> Order:
        return self.ranked_asks.pop(0)
