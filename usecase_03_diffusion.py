# USECASE [03] Simulate diffusion process of "oracle" prices of
# external arbitrageur.

import logging
from exchange_single_maker import ExchangeSingleMaker
from makers.maker_zero_knowledge import MakerZeroKnowledge
from makers.maker_delta import MakerDelta
from makers.maker_replication import MakerReplication
import pandas as pd
import plotly.express as px
from simul.path_generators import geom_brownian_path
import utils_black_scholes as bs


logging.basicConfig(level=logging.DEBUG)

MATURITY = 1.0
NB_DAY_Y = 252
NB_SIM_D = 1

# wrap geometrical path generator
def spawn_path():
    return geom_brownian_path(
        initPrice=100,
        yearlyDrift=0.05,
        yearlyVolat=0.2,
        numDaysToSimul=MATURITY * NB_DAY_Y,
        numStepPerDay=NB_SIM_D,
        numDaysPerYearConvention=NB_DAY_Y,
    )


# set maker params
px_init = 100
tick = 0.5
numBids = numOffers = int(40 / tick)
size = 2 / (numBids + numOffers)


def get_maker_delta(num_offers: int, tick_interval: float) -> MakerDelta:
    maker = MakerDelta(
        px_init,
        lambda x: -bs.delta(x, 100, 1, 0, 0.2),
        num_offers,
        tick_interval,
    )
    return maker


def get_maker_repli_hedged(num_offers: int, tick_interval: float) -> MakerReplication:
    maker = MakerReplication(
        px_init,
        lambda x, t: -bs.delta(x, 120, t, 0, 0.2),
        maturity=MATURITY,
        numOneWayOffers=num_offers,
        tickInterval=tick_interval,
    )
    return maker


# wrap arbitrage logic
def simul_one_path():

    makers = {}
    # makers["delta_0.5_1"] = get_maker_delta(1, 0.5)
    # makers["delta_1.0_1"] = get_maker_delta(1, 1.0)
    # makers["delta_0.5_4"] = get_maker_delta(4, 0.5)
    # makers["delta_2.0_1"] = get_maker_delta(1, 2.0)
    makers["repli_0.5_4"] = get_maker_repli_hedged(8, 0.5)
    # makers["repli_0.5_1"] = get_maker_repli_hedged(1, 0.5)
    # makers["repli_2.0_1"] = get_maker_repli_hedged(1, 2.0)
    # makers["repli_0.2_20"] = get_maker_repli_hedged(20, 0.2)

    exchanges = {}
    for k, v in makers.items():
        exchanges[k] = ExchangeSingleMaker(v)

    path = spawn_path()
    time = 0
    dt = 1 / NB_SIM_D / NB_DAY_Y
    for price in path:
        time += dt
        for x in exchanges.values():
            x.apply_arbitrage(price, time)

    res = []
    for k, v in exchanges.items():
        res.append(
            [
                k,
                path[-1],
                v.maker.cash,
                v.maker.asset,
                len(v.transactions),
            ]
        )
    return pd.DataFrame(res, columns=["maker", "price", "cash", "asset", "nb_tx"])


# monte carlo
data = []
for i in range(200):
    if i % 100 == 0:
        logging.debug("Computing step: {}".format(i))
    pnls = simul_one_path()
    data.append(pnls)

sims = pd.concat(data)
sims["pnl"] = sims["price"] * sims["asset"] + sims["cash"]

px.scatter(sims, x="price", y="asset", color="maker").add_hline(y=0).show()

# plotting E[ pnl_T | price_T ]
px.scatter(sims, x="price", y="pnl", color="maker").add_hline(y=0).show()

# px.line(spawn_path()).show()
