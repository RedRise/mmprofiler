from makers.maker_delta import MakerDelta
from math import isclose

TEST_ABS_TOL = 1E-5


def isclose_loc(x, y):
    return isclose(x, y, abs_tol=TEST_ABS_TOL)


def test_init_tick_interval():
    maker = MakerDelta(100, lambda x: 100 * 100 / x, 0.5, 5, 1)
    assert isclose(maker.midPrice, 100, abs_tol=1E-7)
    assert maker.offersLists.has_bid()
    assert maker.offersLists.has_ask()


def test_take_at_first_rank():
    maker = MakerDelta(100, lambda x: 100 * 100 / x, 0.5, 5, 1)
    assert isclose_loc(maker.midPrice, 100)
    assert maker.offersLists.has_bid()
    assert maker.offersLists.has_ask()

    best_ask = maker.offersLists.get_best_ask()
    tx1 = maker.buy_at_first_rank()
    assert tx1.price == best_ask.price
    assert tx1.quantity == best_ask.quantity

    best_bid = maker.offersLists.get_best_bid()
    tx2 = maker.sell_at_first_rank()
    assert tx2.price == best_bid.price
    assert abs(tx2.quantity) == best_bid.quantity
    assert tx2.quantity < 0


def test_liquidity_reposted():

    maker = MakerDelta(100, lambda x: 100 * 100 / x, 0.5, 5, 1)

    bid1 = maker.offersLists.get_best_bid()
    assert bid1.price == 99.5

    tx = maker.sell_at_first_rank()
    assert tx.price == 99.5
    assert isclose_loc(tx.quantity, -0.50251)

    bid2 = maker.offersLists.get_best_bid()
    assert bid2.price == 99

    tx2 = maker.buy_at_first_rank()
    assert tx2.price == 100
    assert isclose_loc(tx2.quantity, 0.50251)

    bid3 = maker.offersLists.get_best_bid()
    assert bid3.price == 99.5

    ask1 = maker.offersLists.get_best_ask()
    assert ask1.price == 100.5


def test_ccash_and_asset_position():

    maker = MakerDelta(100, lambda x: 100 * 100 / x, 0.5, 5, 1)

    assert maker.asset == 0
    assert maker.cash == 0

    _ = maker.buy_at_first_rank()
    assert isclose_loc(maker.cash, 50)
    assert isclose_loc(maker.asset, -0.49751)

    _ = maker.sell_at_first_rank()
    assert isclose_loc(maker.cash, 0.248756)
    assert isclose_loc(maker.asset, 0)


# # print(maker.offersLists)
