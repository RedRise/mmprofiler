from models.order import Order, OrderType
import logging
from typing import List
# from math import isclose

class OffersLists():
    
    ranked_bids  : List[Order] = []
    ranked_offers : List[Order] = []
    
    def __init__(self) -> None:
        self.ranked_bids = []
        self.ranked_offers = []

    def __str__(self) -> str:

        hline_template = "{:-^15}|{:-^15}||{:-^15}|{:-^15}\n"
        header_template = "{:^15}|{:^15}||{:^15}|{:^15}\n"
        info_template = "{:^15}|{:^15}||{:^15}|{:^15}\n"
        
        hline = hline_template.format("","","","", fill="-")

        result = hline
        result += header_template.format("Qty Bid", "Px Bid", "Px Ask", "Qty Ask")
        result += hline

        for i in range(0, min([5, max(len(self.ranked_bids), len(self.ranked_offers))])):
            bid = self.ranked_bids[i] if len(self.ranked_bids) > i else None
            ask = self.ranked_offers[i] if len(self.ranked_offers) > i else None
            result += info_template.format(
                "{:.5f}".format(bid.quantity) if bid else "", 
                "{:.5f}".format(bid.price) if bid else "", 
                "{:.5f}".format(ask.price) if ask else "", 
                "{:.5f}".format(ask.quantity) if ask else ""
            )

        return result

    def push_maker_order(self, order: Order):

        if (order.OrderType == OrderType.BUY):
            self.ranked_bids.append(order)
        elif (order.OrderType == OrderType.SELL):
            self.ranked_offers.append(order)
        else:
            logging.info("Order type not recognized, nothing pushed.")
    
    def has_bid(self) -> bool:
        return len(self.ranked_bids) > 0
    
    def has_offer(self) -> bool:
        return len(self.ranked_offers) > 0

    def get_best_offer(self) -> Order:
        if self.has_offer():
            return self.ranked_offers[0]
        else:
            return None

    def get_best_bid(self) -> Order:
        if self.has_bid():
            return self.ranked_bids[0]
        else:
            return None
    
    def pop_best_bid(self) -> Order:
        return self.ranked_bids.pop(0)

    def pop_best_offer(self) -> Order:
        return self.ranked_offers.pop(0)



