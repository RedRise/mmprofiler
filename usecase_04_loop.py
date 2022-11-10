# USECASE [04] loop tester
# Display Order Quantities after and Before loop price processing

import pandas as pd
from exchange_single_maker import ExchangeSingleMaker
from makers.maker_zero_knowledge import MakerZeroKnowledge
import plotly.express as px
from utils import orderbook_to_dataframe


maker = MakerZeroKnowledge(
    initMidPrice=100, tickSize=0.5, numBids=20, sizeBid=0.1, numOffers=20, sizeOffer=0.1
)
exchange = ExchangeSingleMaker(maker)
print(exchange.offers)

# exchange.apply_arbitrage(110)
# print(exchange.orderBook)

# exchange.apply_arbitrage(108)

obdf1 = orderbook_to_dataframe(exchange.offers)
obdf1["time"] = "init"

price_loop = [111, 95, 100]
for price in price_loop:
    exchange.apply_arbitrage(price)

obdf2 = orderbook_to_dataframe(exchange.offers)
obdf2["time"] = "after"

# obdf_wide = obdf1.set_index("price").join(obdf2.set_index("price"), lsuffix="_init", rsuffix="_term")

obdf_long = pd.concat([obdf1, obdf2], axis=0)

fig = px.bar(obdf_long, x="price", y="quantity", color="time", barmode="group")
fig.show()
