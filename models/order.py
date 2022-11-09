from enum import Enum
import uuid
from math import isclose
from functools import total_ordering

TOLERANCE = 1E-7


class OrderType(Enum):
    BUY = 0
    SELL = 1

    def __str__(self):
        return self.name


@total_ordering
class Order():

    def __init__(self, orderType: OrderType, price: float, quantity: float) -> None:
        self.uuid = uuid.uuid4()

        self.order_type = orderType
        if price <= 0 or quantity <= 0:
            raise(ValueError("Price and Quantity"))
        self.price = price
        self.quantity = quantity

    def __str__(self) -> str:
        return "{type} {quantity}@{price}".format(
            type=self.order_type,
            quantity=self.quantity,
            price=self.price
        )

    def __eq__(self, obj):
        return isinstance(obj, Order) and obj.order_type == self.order_type \
            and isclose(obj.price, self.price, rel_tol=TOLERANCE) \
            and isclose(obj.quantity, self.quantity, rel_tol=TOLERANCE) \
            and obj.uuid == self.uuid

    def __lt__(self, obj):
        if not isinstance(obj, Order):
            return False
        if self.order_type == obj.order_type:
            return (self.price < obj.price) ^ (self.order_type == OrderType.BUY)
        else:
            return (self.price < obj.price)
