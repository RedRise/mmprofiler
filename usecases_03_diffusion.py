# USECASE [03] Simulate diffusion process of "oracle" prices of
# external arbitrageur.

import logging
from math import sqrt
from exchange_single_maker import ExchangeSingleMaker
from makers.single_maker_zero_knowledge import SingleMakerZeroKnowledge
from utils import compute_maker_pnl
import pandas as pd
import plotly.express as px
from numpy.random import default_rng
import copy

px_min = 60
px_max = 140
tick = 0.5
init_qty = 2/round((px_max-px_min)/tick, 0)

maker = SingleMakerZeroKnowledge(px_min, px_max, tick, init_qty)
exchange = ExchangeSingleMaker(maker)
print(exchange.orderBook)
# num_year = 1/12
# step_day_size = 1.0/24
# year_drift = 0.1
# year_volat = 0.40

def simul_diffusion(exchange, num_year, step_day_size, year_drift, year_volat):
    """ Simulate diffusion with 
    :param exchange: an instantiated exchange
    :param num_year: number of years of simulation
    :param step_day_size: step size in day (eg 1/24 = 1 point per hour)
    :param year_drift: annual drift of the diffusion (eg 0.1)
    "param year_volat: annual volatility of the diffusion (eg 0.2)
    """
    
    num_step = int(num_year * 252 / step_day_size)
    step_drift = year_drift * step_day_size / 252
    step_volat = year_volat / sqrt(1/step_day_size * 252)

    rng = default_rng()
    sim_normal = rng.normal(step_drift, step_volat, num_step)

    sim_price = exchange.maker.midPrice
    for e in sim_normal:
        sim_price *= (1+e)
        exchange.apply_arbitrage(sim_price)

    return (sim_price, compute_maker_pnl(exchange.transactions))

data = []
for i in range(1000):
    if i % 100 == 0:
        logging.info("Computing step: {}".format(i))
    px_min, px_max, tick = 60, 140, 0.5
    pnls = simul_diffusion(copy.deepcopy(exchange), 1/12, 1.0/10, 0.1, 0.4)
    data.append(pnls)

# plotting E[ pnl_T | price_T ]
sims = pd.DataFrame(data, columns=["price", "pnl"]).sort_values("price")
px.scatter(x=sims["price"], y=sims["pnl"]).add_hline(y=0).show()

# px.histogram(sims, x="price").show()
px.histogram(sims, x="pnl").add_vline(x=0).show()


print(exchange.orderBook)