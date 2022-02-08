from enum import Enum
from uuid import UUID, uuid4
import logging

from pyparsing import Or
from models.order import Order, OrderType


# Transaction (seen from the taker perspective)
class Transaction():

    price: float
    signedQuantity: float

    def __init__(self, order_ref: UUID, price: float, quantity: float) -> None:
        self.uuid = uuid4()
        self.price = price
        self.quantity = quantity

    def __str__(self) -> str:
        return "[tx] {} {:.5f} @ {:.5f}".format(
            "BUY" if self.quantity > 0 else "SELL",
            abs(self.quantity),
            self.price
        )


def take_maker_order(order: Order) -> Transaction:

    if order.OrderType == OrderType.SELL:
        signed_quantity = order.quantity
    elif order.OrderType == OrderType.BUY:
        signed_quantity = - order.quantity
    else:
        logging.error("OrderType not recognized.")
        return None

    return Transaction(order.uuid, order.price, signed_quantity)
