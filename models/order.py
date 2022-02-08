from enum import Enum
import uuid
from math import isclose

from more_itertools import quantify

TOLERANCE = 1E-7

class OrderType(Enum):
    BUY = 0
    SELL = 1

    def __str__(self):
        return self.name

class Order():

    def __init__(self, orderType : OrderType, price: float, quantity: float, gas: float) -> None:
        self.uuid = uuid.uuid4()

        self.OrderType = orderType
        if price <= 0 or quantity <=0:
            raise(ValueError("Price and Quantity"))
        self.Price = price
        self.Quantity = quantity
        self.Gas = gas
    

    def __str__(self) -> str:
        return "{type} {quantity}@{price}".format(
            type = self.OrderType,
            quantity = self.Quantity,
            price = self.Price
        )

    def __eq__(self, obj):
        return isinstance(obj, Order) and  obj.OrderType == self.OrderType \
            and isclose(obj.Price, self.Price, rel_tol=TOLERANCE) \
            and isclose(obj.Quantity, self.Quantity, rel_tol=TOLERANCE) \
            and isclose(obj.Gas , self.Gas, rel_tol=TOLERANCE) \
            and obj.uuid == self.uuid
    