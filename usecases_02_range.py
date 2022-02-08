# USECASE [02] Iterating through a range of prices to plot maker pnl

from exchange_single_maker import ExchangeSingleMaker
from makers.single_maker_zero_knowledge import SingleMakerZeroKnowledge
from utils import compute_maker_pnl, compute_maker_pnls, plot_pnl
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from numpy.random import default_rng

px_min = 60
px_max = 140
tick = 0.5
init_qty = 2/round((px_max-px_min)/tick, 0)

# buy until px_max
maker = SingleMakerZeroKnowledge(px_min, px_max, tick, init_qty)
exchange = ExchangeSingleMaker(maker)

while True:
    tx = exchange.buy_at_first_rank()
    if not tx or tx.price > px_max:
        break
pnl_up = compute_maker_pnls(exchange.transactions)

# sell until px_min
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
# simple projection on 2nd order polynomial
m = np.poly1d(np.polyfit(x, y, 2))(x)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y,
                    mode='lines',
                    name='pnl'))
fig.add_trace(go.Scatter(x=x, y=m,
                    mode='markers',
                    name='poly2'))
fig.show()


