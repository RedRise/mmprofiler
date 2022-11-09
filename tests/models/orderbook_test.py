import pytest
from models.orderbook import Order, OrderBook, OrderType
import copy


def test_push_order():
    orderBook = OrderBook(0.1)
    assert orderBook is not None
    assert not orderBook.has_bid()
    assert not orderBook.has_ask()

    offer = Order(OrderType.SELL, 1, 2, 3)
    orderBook.append_maker_order(copy.copy(offer))
    assert not orderBook.has_bid()
    assert orderBook.has_ask()
    assert offer == orderBook.get_best_ask()

    bid = Order(OrderType.BUY, 10, 1, 2)
    orderBook.append_maker_order(copy.copy(bid))
    assert bid == orderBook.get_best_bid()


def test_append_not_worst():
    orderbook = OrderBook(0.1)
    orderbook.append_maker_order(Order(OrderType.SELL, 1, 2, 3))
    assert orderbook.has_ask()

    with pytest.raises(Exception):
        orderbook.append_maker_order(Order(OrderType.SELL, 0.5, 2, 3))
