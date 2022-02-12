# USECASE [03] Simulate diffusion process of "oracle" prices of
# external arbitrageur.

import logging
from exchange_single_maker import ExchangeSingleMaker
from makers.single_maker_zero_knowledge import SingleMakerZeroKnowledge
import pandas as pd
import plotly.express as px
from simul.path_generators import geom_brownian_path

logging.basicConfig(level=logging.DEBUG)

# wrap geometrical path generator
def spawn_path():
    return geom_brownian_path(
        initPrice=100,
        yearlyDrift=0.1,
        yearlyVolat=0.4,
        numDaysToSimul=120,
        numStepPerDay=8
    )


# set maker params
px_init = 100
tick = 0.5
numBids = numOffers = int(40/tick)
size = 2 / (numBids+numOffers)


# wrap arbitrage logic
def simul_one_path():

    maker = SingleMakerZeroKnowledge(
        initMidPrice=px_init, 
        tickSize=tick,
        numBids=numBids, 
        sizeBid=size, 
        numOffers=numOffers, 
        sizeOffer=size
    )

    exchange = ExchangeSingleMaker(maker)

    path = spawn_path()
    for price in path:
        exchange.apply_arbitrage(price)

    return (path[-1], exchange.maker.cash, exchange.maker.asset, len(exchange.transactions))


# monte carlo
data = []
for i in range(1000):
    if i % 100 == 0:
        logging.debug("Computing step: {}".format(i))
    pnls = simul_one_path()
    data.append(pnls)

# cast results under nice dataframe
sims = pd.DataFrame(data, columns=["price", "cash", "asset", "num_tx"])
sims["pnl"] = sims["price"]*sims["asset"] + sims["cash"]

# plotting E[ pnl_T | price_T ]
px.scatter(x=sims["price"], y=sims["pnl"]).add_hline(y=0).show()

# px.histogram(sims, x="price").show()
px.histogram(sims, x="pnl").add_vline(x=0).show()

