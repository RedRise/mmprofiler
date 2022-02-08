from models.orderbook import Order, OrderBook, OrderType
import copy

def test_push_order():
    orderBook = OrderBook(0.1)
    assert orderBook is not None
    assert not orderBook.has_bid()
    assert not orderBook.has_offer()

    offer = Order(OrderType.SELL, 1, 2, 3)
    orderBook.push_maker_order(copy.copy(offer))
    assert not orderBook.has_bid()
    assert orderBook.has_offer()
    assert offer == orderBook.get_best_offer()

    bid = Order(OrderType.BUY, 10, 1, 2)
    orderBook.push_maker_order(copy.copy(bid))
    assert bid == orderBook.get_best_bid()


