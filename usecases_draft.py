import logging
from math import sqrt
from mimetypes import init
from exchange_single_maker import ExchangeSingleMaker
from makers.single_maker_zero_knowledge import SingleMakerZeroKnowledge
from utils import compute_maker_pnl, compute_maker_pnls, plot_pnl
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from numpy.random import default_rng
import logging


# USECASE 1/ manual testing
maker = SingleMakerZeroKnowledge(90, 110, 0.5, 1)
exchange = ExchangeSingleMaker(maker)

exchange.buy_at_first_rank()
print(exchange.orderBook)
exchange.sell_at_first_rank()
print(exchange.orderBook)


# USECASE 2/ through range profile
px_min = 60
px_max = 140
tick = 0.5
init_qty = 2/round((px_max-px_min)/tick, 0)

# buy
maker = SingleMakerZeroKnowledge(px_min, px_max, tick, init_qty)
exchange = ExchangeSingleMaker(maker)

while True:
    tx = exchange.buy_at_first_rank()
    if not tx or tx.price > px_max:
        break
pnl_up = compute_maker_pnls(exchange.transactions)

# sell
maker = SingleMakerZeroKnowledge(px_min, px_max, tick, init_qty)
exchange = ExchangeSingleMaker(maker)
while True:
    tx = exchange.sell_at_first_rank()
    if not tx or tx.price < px_min:
        break
pnl_down = compute_maker_pnls(exchange.transactions)

taker_pnls = pd.concat([pnl_down, pnl_up], axis=0).sort_values("price")

x = taker_pnls["price"]
y = taker_pnls["pnl"]
m = np.poly1d(np.polyfit(x, y, 2))(x)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y,
                    mode='lines',
                    name='pnl'))
fig.add_trace(go.Scatter(x=x, y=m,
                    mode='markers',
                    name='poly2'))
fig.show()


# USECASE 3/ simulation


# px_min = 60
# px_max = 140
# tick = 0.5
# init_qty = 2/round((px_max-px_min)/tick, 0)
# num_year = 1/12
# step_day_size = 1.0/24
# year_drift = 0.1
# year_volat = 0.40

def simul_diffusion(px_min, px_max, tick, init_qty, num_year, step_day_size, year_drift, year_volat):
    num_step = int(num_year * 252 / step_day_size)
    step_drift = year_drift * step_day_size / 252
    step_volat = year_volat / sqrt(1/step_day_size * 252)

    maker = SingleMakerZeroKnowledge(px_min, px_max, tick, init_qty)
    exchange = ExchangeSingleMaker(maker)

    rng = default_rng()
    sim_normal = rng.normal(step_drift, step_volat, num_step)

    sim_price = exchange.maker.midPrice
    for e in sim_normal:
        sim_price *= (1+e)
        exchange.apply_arbitrage(sim_price)

    return (sim_price, compute_maker_pnl(exchange.transactions))

data = []
for i in range(10000):
    if i % 100 == 0:
        logging.info("Computing step: {}".format(i))
    px_min, px_max, tick = 60, 140, 0.5
    pnls = simul_diffusion(px_min, px_max, tick, 2/round((px_max-px_min)/tick, 0), 1/12, 1.0/10, 0.1, 0.4)
    data.append(pnls)

sims = pd.DataFrame(data, columns=["price", "pnl"]).sort_values("price")
px.scatter(x=sims["price"], y=sims["pnl"]).add_hline(y=0).show()

px.histogram(sims, x="price").show()
px.histogram(sims, x="pnl").add_vline(x=0).show()
