import plotly.graph_objects as go
import pandas as pd


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
