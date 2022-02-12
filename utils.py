import plotly.graph_objects as go
import pandas as pd
from pyparsing import col
from models.orderbook import OrderBook


def compute_maker_pnl(transactions):
    cash = 0
    asset = 0
    for tx in transactions:
        asset -= tx.quantity
        cash += tx.quantity*tx.price

    return asset*transactions[-1].price+cash


def compute_maker_pnls(transactions) -> pd.DataFrame:
    pnls = []
    cash = 0
    asset = 0

    data = []
    for tx in transactions:
        asset -= tx.quantity
        cash += tx.quantity*tx.price
        data.append((cash, asset, tx.price, asset*tx.price+cash))

    return pd.DataFrame(data, columns=['cash', 'asset', 'price', 'pnl'])


def plot_pnl(pnls):
    x = pnls['price']
    y = pnls['pnl']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y,
                             mode='lines',
                             name='pnl'))
    fig.show()



def orderbook_to_dataframe(ob : OrderBook) -> pd.DataFrame:
    bids = [(x.price, x.quantity) for x in ob.ranked_bids]
    asks = [(x.price, -x.quantity) for x in ob.ranked_offers]
    bids.extend(asks)

    result = pd.DataFrame(bids, columns=["price", "quantity"])
    return result.sort_values("price")
