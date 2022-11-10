from models.order import Order, OrderType
from models.offers_lists import OffersLists
import copy


def test_push_order():
    offersLists = OffersLists()
    assert offersLists is not None
    assert not offersLists.has_bid()
    assert not offersLists.has_ask()

    offer = Order(OrderType.SELL, 110, 2)
    offersLists.add_order(copy.copy(offer))
    assert not offersLists.has_bid()
    assert offersLists.has_ask()
    assert offer == offersLists.get_best_ask()

    bid = Order(OrderType.BUY, 100, 1)
    offersLists.add_order(copy.copy(bid))
    assert bid == offersLists.get_best_bid()


def test_append_best_bid():
    offersLists = OffersLists()
    offersLists.add_order(Order(OrderType.BUY, 100, 2))
    assert offersLists.get_best_bid().price == 100

    offersLists.add_order(Order(OrderType.BUY, 110, 1))
    assert offersLists.get_best_bid().price == 110


def test_append_best_ask():
    offersLists = OffersLists()
    offersLists.add_order(Order(OrderType.SELL, 110, 2))
    assert offersLists.get_best_ask().price == 110

    offersLists.add_order(Order(OrderType.SELL, 100, 1))
    assert offersLists.get_best_ask().price == 100


def test_add_worst_bid():
    offersLists = OffersLists()
    offersLists.add_order(Order(OrderType.BUY, 100, 2))
    assert offersLists.get_best_bid().price == 100

    offersLists.add_order(Order(OrderType.BUY, 90, 1))
    assert offersLists.get_best_bid().price == 100


def test_add_worst_ask():
    offersLists = OffersLists()
    offersLists.add_order(Order(OrderType.SELL, 110, 2))
    assert offersLists.get_best_ask().price == 110

    offersLists.add_order(Order(OrderType.SELL, 120, 1))
    assert offersLists.get_best_ask().price == 110
