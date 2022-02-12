# USECASE [02] Iterating through a range of prices to plot maker pnl

from exchange_single_maker import ExchangeSingleMaker
from makers.single_maker_zero_knowledge import SingleMakerZeroKnowledge
from utils import compute_maker_pnls
import pandas as pd
import numpy as np
import plotly.graph_objects as go

px_init = 100
tick = 0.5
numBids = numOffers = int(40/tick)
size = 2 / (numBids+numOffers)

maker = SingleMakerZeroKnowledge(initMidPrice=px_init, tickSize=tick, numBids=numBids, sizeBid=size, numOffers=numOffers, sizeOffer=size)
exchange = ExchangeSingleMaker(maker)

while True:
    tx = exchange.buy_at_first_rank()
    if not tx:
        break
pnl_up = compute_maker_pnls(exchange.transactions)

# sell until px_min
maker = SingleMakerZeroKnowledge(initMidPrice=px_init, tickSize=tick, numBids=numBids, sizeBid=size, numOffers=numOffers, sizeOffer=size)
exchange = ExchangeSingleMaker(maker)
while True:
    tx = exchange.sell_at_first_rank()
    if not tx:
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
