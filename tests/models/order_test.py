import pytest
from models.order import OrderType, Order


def test_order_buy():
    order = Order(OrderType.BUY, 1, 2)

    assert order.order_type == OrderType.BUY
    assert order.price == 1
    assert order.quantity == 2


def test_order_negative_quantity_fails():
    with pytest.raises(ValueError) as exception_info:
        order = Order(OrderType.BUY, 1, -2)
    assert "ValueError" in str(exception_info.type)


def test_order_negative_price_fails():
    with pytest.raises(ValueError) as exception_info:
        order = Order(OrderType.BUY, -1, 2)
    assert "ValueError" in str(exception_info.type)


def test_order_comparaison_buys():
    assert Order(OrderType.BUY, 100, 1) < Order(OrderType.BUY, 99, 1)


def test_order_comparaison_sells():
    assert Order(OrderType.SELL, 100, 1) < Order(OrderType.SELL, 101, 1)


def test_order_comparaison_buy_sell():

    assert Order(OrderType.BUY, 100, 1) < Order(OrderType.SELL, 101, 1)
    assert Order(OrderType.SELL, 100, 1) < Order(OrderType.BUY, 101, 1)
