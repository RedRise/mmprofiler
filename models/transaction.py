from uuid import UUID, uuid4
import logging

from models.order import Order, OrderType


# Transaction (seen from the taker perspective)
class Transaction:

    price: float
    time: float

    def __init__(
        self, order_ref: UUID, price: float, quantity: float, time: float
    ) -> None:
        self.uuid = uuid4()
        self.price = price
        self.quantity = quantity
        self.time = time

    def __str__(self) -> str:
        return "[tx] t:{:.4f} {} {:.4f} @{:.4f}".format(
            self.time if self.time else -1,
            "BUY " if self.quantity > 0 else "SELL",
            abs(self.quantity),
            self.price,
        )

    def __repr__(self) -> str:
        return self.__str__()


def take_maker_order(order: Order, time: float = None) -> Transaction:

    if order.order_type == OrderType.SELL:
        signed_quantity = order.quantity
    elif order.order_type == OrderType.BUY:
        signed_quantity = -order.quantity
    else:
        logging.error("OrderType not recognized.")
        return None

    return Transaction(order.uuid, order.price, signed_quantity, time)
