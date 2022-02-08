from asyncio import SendfileNotAvailableError
from queue import PriorityQueue
from makers.single_maker_zero_knowledge import SingleMakerZeroKnowledge
from models.transaction import Transaction
from models.orderbook import Order
from math import isclose


def test_init():
    maker = SingleMakerZeroKnowledge(99, 102, 1, 1)
    assert isclose(maker.midPrice, 100.5, abs_tol=1E-7)
    assert maker.orderBook.tickSize == 1
    assert maker.orderBook.has_bid()
    assert maker.orderBook.has_offer()


def test_take_at_first_rank():
    maker = SingleMakerZeroKnowledge(90, 110, 0.5, 1)
    assert maker.orderBook.has_bid()
    assert maker.orderBook.has_offer()

    best_offer = maker.orderBook.get_best_offer()
    tx1 = maker.buy_at_first_rank()
    assert tx1.price == best_offer.Price
    assert tx1.quantity == best_offer.Quantity

    best_bid = maker.orderBook.get_best_bid()
    tx2 = maker.sell_at_first_rank()
    assert tx2.price == best_bid.Price
    assert abs(tx2.quantity) == best_bid.Quantity
    assert tx2.quantity < 0


def test_liquidity_reposted():

    maker = SingleMakerZeroKnowledge(90, 110, 0.5, 1)

    assert maker.orderBook.has_offer()
    assert maker.orderBook.has_bid()

    bid1 = maker.orderBook.get_best_bid()
    assert bid1.Price == 99.5

    tx = maker.sell_at_first_rank()
    assert tx.price == 99.5
    assert tx.quantity == -1

    bid2 = maker.orderBook.get_best_bid()
    assert bid2.Price == 99

    tx2 = maker.buy_at_first_rank()
    assert tx2.price == 100
    assert tx2.quantity > 1

    bid3 = maker.orderBook.get_best_bid()
    assert bid3.Price == 99.5

    ask1 = maker.orderBook.get_best_offer()
    assert ask1.Price == 100.5


def test_ccash_and_asset_position():

    maker = SingleMakerZeroKnowledge(90, 110, 0.5, 1)

    assert maker.asset == 0
    assert maker.cash == 0

    _ = maker.buy_at_first_rank()
    assert maker.cash == 100
    assert maker.asset == -1

    _ = maker.buy_at_first_rank()
    assert maker.cash == 200.5
    assert maker.asset == -2

    maker = SingleMakerZeroKnowledge(90, 110, 0.5, 1)

    assert maker.asset == 0
    assert maker.cash == 0

    _ = maker.sell_at_first_rank()
    assert maker.cash == -99.5
    assert maker.asset == 1

    _ = maker.sell_at_first_rank()
    assert maker.cash == -198.5
    assert maker.asset == 2
