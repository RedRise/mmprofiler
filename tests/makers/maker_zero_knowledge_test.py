from makers.maker_zero_knowledge import MakerZeroKnowledge
from math import isclose


def test_init():

    maker = MakerZeroKnowledge(100, 1, 2, 1, 2, 1)
    assert isclose(maker.midPrice, 100, abs_tol=1e-7)
    assert maker.tickSize == 1
    assert maker.offers.has_bid()
    assert maker.offers.has_ask()


def test_take_at_first_rank():
    maker = MakerZeroKnowledge(100, 1, 20, 0.5, 20, 0.5)
    assert isclose(maker.midPrice, 100, abs_tol=1e-7)
    assert maker.offers.has_bid()
    assert maker.offers.has_ask()

    best_offer = maker.offers.get_best_ask()
    tx1 = maker.buy_at_first_rank()
    assert tx1.price == best_offer.price
    assert tx1.quantity == best_offer.quantity

    best_bid = maker.offers.get_best_bid()
    tx2 = maker.sell_at_first_rank()
    assert tx2.price == best_bid.price
    assert abs(tx2.quantity) == best_bid.quantity
    assert tx2.quantity < 0


def test_liquidity_reposted():

    maker = MakerZeroKnowledge(100, 0.5, 20, 1, 20, 1)

    assert maker.offers.has_ask()
    assert maker.offers.has_bid()

    bid1 = maker.offers.get_best_bid()
    assert bid1.price == 99.5

    tx = maker.sell_at_first_rank()
    assert tx.price == 99.5
    assert tx.quantity == -1

    bid2 = maker.offers.get_best_bid()
    assert bid2.price == 99

    tx2 = maker.buy_at_first_rank()
    assert tx2.price == 100
    assert isclose(tx2.quantity, 0.995)

    bid3 = maker.offers.get_best_bid()
    assert bid3.price == 99.5

    ask1 = maker.offers.get_best_ask()
    assert ask1.price == 100.5


def test_ccash_and_asset_position():

    maker = MakerZeroKnowledge(100, 0.5, 20, 1, 20, 1)

    assert maker.asset == 0
    assert maker.cash == 0

    _ = maker.buy_at_first_rank()
    assert maker.cash == 100.5
    assert maker.asset == -1

    _ = maker.buy_at_first_rank()
    assert maker.cash == 201.5
    assert maker.asset == -2

    maker = MakerZeroKnowledge(100, 0.5, 20, 1, 20, 1)

    assert maker.asset == 0
    assert maker.cash == 0

    _ = maker.sell_at_first_rank()
    assert maker.cash == -99.5
    assert maker.asset == 1

    _ = maker.sell_at_first_rank()
    assert maker.cash == -198.5
    assert maker.asset == 2
