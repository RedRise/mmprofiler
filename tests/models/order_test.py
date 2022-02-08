import pytest
from models.order import OrderType, Order

def test_order_buy():
    order = Order(OrderType.BUY, 1, 2, 3)

    assert order.OrderType == OrderType.BUY
    assert order.price == 1
    assert order.quantity == 2
    assert order.gas == 3

def test_order_negative_quantity_fails():
    with pytest.raises(ValueError) as exception_info:
        order = Order(OrderType.BUY, 1, -2, 3)
    assert "ValueError" in str(exception_info.type)

def test_order_negative_price_fails():
    with pytest.raises(ValueError) as exception_info:
        order = Order(OrderType.BUY, -1, 2, 3)
    assert "ValueError" in str(exception_info.type)

