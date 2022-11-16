import plotly.graph_objects as go
import pandas as pd
from models.offers_lists import OffersLists
from models.transaction import Transaction
from typing import List


def compute_maker_pnl(transactions):
    cash = 0
    asset = 0
    for tx in transactions:
        asset -= tx.quantity
        cash += tx.quantity * tx.price

    return asset * transactions[-1].price + cash


def compute_maker_pnls(transactions) -> pd.DataFrame:
    pnls = []
    cash = 0
    asset = 0

    data = []
    for tx in transactions:
        asset -= tx.quantity
        cash += tx.quantity * tx.price
        data.append((cash, asset, tx.price, asset * tx.price + cash))

    return pd.DataFrame(data, columns=["cash", "asset", "price", "pnl"])


def plot_pnl(pnls):
    x = pnls["price"]
    y = pnls["pnl"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="pnl"))
    fig.show()


def offers_to_dataframe(offers: OffersLists) -> pd.DataFrame:
    bids = [(x.price, x.quantity, "BID") for x in offers.ranked_bids]
    asks = [(x.price, x.quantity, "ASK") for x in offers.ranked_asks]
    bids.extend(asks)

    result = pd.DataFrame(bids, columns=["price", "quantity", "way"])

    return result.sort_values("price", ascending=False)


def transactions_to_dataframe(txs: List[Transaction]) -> pd.DataFrame:
    values = [(tx.time, tx.price, tx.quantity) for tx in txs]
    return pd.DataFrame(values, columns=["time", "price", "quantity"])
