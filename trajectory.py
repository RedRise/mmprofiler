import math
from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import utils as ut
import utils_black_scholes as bs
from exchange_single_maker import ExchangeSingleMaker
from makers.maker_delta import MakerDelta
from models.transaction import Transaction
from simul.path_generators import geom_brownian_path

# CONSTANTS -------------------------------------------------------------------

NB_DAY_PER_YEAR = 252

# STREAMLIT CONFIG ------------------------------------------------------------

st.set_page_config(layout="wide")

# STREAMLIT STATE -------------------------------------------------------------

## State Variable Names

sExchange = "exchange"
sTimeIdx = "time_index"
sTime = "time"
sTimeIdxNxt = "time_index_nxt"
sTimeOver = "time_over"
sPxCur = "px_cur"
sPxNxt = "px_nxt"
sDltCur = "delta_cur"
sDltNxt = "delta_nxt"
sRebuildMaker = "rebuild_maker"


## functions (getter/setter)
def state_set(varName: str, value):
    st.session_state[varName] = value


def state_get(varName: str, default_value=None):
    if varName not in st.session_state:
        state_set(varName, default_value)
    return st.session_state[varName]


def state_context_repr():
    return "σs:{}, K:{} σr:{}, w:{} n:{}".format(
        i_volat, i_strike, i_volat_repli, tickInterval, numOffers
    )


def state_maker_to_rebuild():
    state_set(sRebuildMaker, True)


# STREAMLIT LAYOUT ------------------------------------------------------------

st.title("Market Making with curves")

tabHome, tabTraj, tabCallOption, tabMaker, tabMC = st.tabs(
    ["Home", "Single Path", "Call Option", "Maker", "🎲 Monte Carlo"]
)

## TAB Home ---------------------------

tabHome.write("This app illustrates a market making activity based on curve.")

## TAB TRAJ ---------------------------

st_loc = tabTraj

st_loc.subheader("Simulation parameters")

col1up, _, col2up = st_loc.columns([2, 1, 2])

i_nb_day = col1up.slider("Nb simulated days", 0, 750, 252)
i_nb_step_day = col1up.slider("Nb intraday simulations", 0, 10, 1)
i_seed = col1up.number_input("Seed for diffusion", 0, None, 123)

i_yield = col2up.slider("Yearly return (%)", -10, 50, 10) / 100
i_volat = col2up.slider("Yearly volatility (%)", 1, 80, 20) / 100
i_px_init = col2up.number_input("Initial price", 50.0, 200.0, 100.0, step=1.0)

i_time_delta = 1 / (float(NB_DAY_PER_YEAR) * float(i_nb_step_day))


def simulate_path(seed=None):
    return geom_brownian_path(
        i_px_init, i_yield, i_volat, i_nb_day, i_nb_step_day, NB_DAY_PER_YEAR, seed
    )


i_prices = simulate_path(i_seed)

fig = px.line(
    x=[i_time_delta * i for i in range(0, len(i_prices))],
    y=i_prices,
    labels={"x": "Time (in year)", "y": "Base token price"},
)
# fig.update_yaxes(visible=False)
st_loc.plotly_chart(fig, use_container_width=True)


## TAB CALL OPTION --------------------

st_loc = tabCallOption

st_loc.subheader("Parameters")
st_loc.write(
    "This section describes the target call option to take delta function from. To be more precise, the market making activity will be to hedge a long call position, i.e. we will target - delta position of risky asset."
)

col1up, _, col2up = st_loc.columns([2, 1, 2])


def call_module():
    mat_ratio = (
        col1up.slider(
            "Maturity ratio w.r.t the number of simulated days (%)",
            0,
            100,
            100,
            step=25,
        )
        / 100
    )
    strike = col1up.slider(
        "Strike",
        math.floor(0.10 * i_px_init),
        math.ceil(2 * i_px_init),
        int(i_px_init),
        step=10,
    )
    volat = col2up.slider("Volatility used for replication (%)", 1, 80, 20) / 100
    rate = col2up.slider("Rate used for replication (%)", -2, 20, 0) / 100
    return (mat_ratio, strike, volat, rate)


(i_mat_ratio, i_strike, i_volat_repli, i_rate_repli) = call_module()
i_mat = float(i_mat_ratio) * float(i_nb_day) / float(NB_DAY_PER_YEAR)


def delta_fun(x: float, t: float) -> float:
    return bs.delta(x, i_strike, t, i_rate_repli, i_volat_repli)


char_prices = list(range(math.floor(i_px_init * 0.5), math.ceil(1.5 * i_px_init)))
char_deltas = [delta_fun(x, i_mat) for x in char_prices]
fig = px.line(x=char_prices, y=char_deltas)

st_loc.subheader("Delta Function")
st_loc.plotly_chart(fig, use_container_width=True)


## TAB MAKER --------------------------

st_loc = tabMaker

col1up, _, col2up = st_loc.columns([1, 1, 2])

col1up.subheader("Parameters")

numOffers = col1up.slider(
    "Number of offers (one way)", 1, 10, 3, on_change=state_maker_to_rebuild
)

tickInterval = col1up.number_input(
    "Tick interval to post offers",
    0.25,
    10.0,
    2.0,
    0.25,
    on_change=state_maker_to_rebuild,
)

i_maker_repli = col1up.checkbox("Replication (vs. fixed curve)")

tabFrame, tabPlot = col2up.tabs(["DataFrame", "Chart"])
stMakerTable = tabFrame.empty()
stMakerPlot = tabPlot.empty()

st_loc.markdown("""---""")

col1up, col2up, _, col4 = st_loc.columns([1, 1, 1, 1])


def build_maker(use_latest_price: bool):
    if use_latest_price:
        p0 = st.session_state.get(sPxCur, i_px_init)
    else:
        p0 = i_px_init

    mat_float = float(i_nb_day) * float(i_mat_ratio) / float(NB_DAY_PER_YEAR)
    maker = MakerDelta(
        initMidPrice=p0,
        deltaFunction=lambda x: -delta_fun(x, mat_float),
        numOneWayOffers=numOffers,
        tickInterval=tickInterval,
        tickQuantity=None,
    )
    return maker


def init_exchange():
    maker = build_maker(use_latest_price=True)
    st.session_state[sExchange] = ExchangeSingleMaker(maker)


if sExchange not in st.session_state:
    init_exchange()


def reset_state_time_idx():
    if sTimeIdx in st.session_state:
        del st.session_state[sTimeIdx]
    state_maker_to_rebuild()
    init_exchange()
    update_state_time_idx()


def display_maker():
    offers_dt = ut.offers_to_dataframe(st.session_state[sExchange].offers)
    with stMakerTable:
        st.table(offers_dt)

    with stMakerPlot:
        st.plotly_chart(
            px.bar(offers_dt, x="quantity", y="price", color="way", orientation="h"),
            use_container_width=True,
        )


def update_state_time_idx():
    if not sTimeIdx in st.session_state:
        st.session_state[sTimeIdx] = 0
        st.session_state[sTimeOver] = False

    i = st.session_state[sTimeIdx]
    stss = st.session_state
    stss[sPxCur] = i_prices[i]
    time_idx_next = i + 1 if not stss[sTimeOver] else i
    stss[sTimeIdxNxt] = time_idx_next
    stss[sPxNxt] = i_prices[time_idx_next]

    if state_get(sRebuildMaker, True):
        maker = build_maker(True)
        st.session_state[sExchange].maker = maker
        state_set(sRebuildMaker, False)

    maker = st.session_state[sExchange].maker
    stss[sDltCur] = maker.computeDelta(stss[sPxCur])
    stss[sDltNxt] = maker.computeDelta(stss[sPxNxt])


def time_clock():
    time_idx = min(st.session_state[sTimeIdx] + 1, len(i_prices))
    st.session_state[sTimeIdx] = time_idx
    st.session_state[sTimeOver] = time_idx >= len(i_prices)


def apply_arbitrage():
    st.session_state["exchange"].apply_arbitrage(
        price=st.session_state[sPxNxt],
        time=float(st.session_state[sTimeIdxNxt]) * i_time_delta,
    )
    # set_counters(st.session_state["time_idx_nxt"])
    time_clock()
    update_state_time_idx()


update_state_time_idx()
display_maker()

if col1up.button("Go to next time step"):
    apply_arbitrage()

if col2up.button("Go to end"):
    while state_get(sTimeIdx) < len(i_prices) - 2:
        apply_arbitrage()
    display_maker()

if col4.button("Reset"):
    reset_state_time_idx()
    display_maker()


### Metrics

col1up, col2up, col3, col4 = st_loc.columns(4)
col1up.metric("Current Price", "%.2f" % st.session_state[sPxCur])
col2up.metric("Current Delta", "%.2f" % st.session_state[sDltCur])
col3.metric(
    "Next Price",
    "%.2f" % st.session_state[sPxNxt],
    "%.4f" % (st.session_state[sPxNxt] - st.session_state[sPxCur]),
)
col4.metric(
    "Next Delta",
    "%.2f" % st.session_state[sDltNxt],
    "%.4f" % (st.session_state[sDltNxt] - st.session_state[sDltCur]),
)

tabMakerAssets, tabMakerAssets3D, tabTxs, tabDebug = st_loc.tabs(
    ["Maker assets", "Maker assets 3D", "Taker transactions", "[debug_state]"]
)

tabDebug.write(st.session_state)

tabTxs.write(st.session_state["exchange"].transactions)

# https://plotly.com/python/line-charts/#interpolation-with-line-plots


txs: List[Transaction]
txs = st.session_state["exchange"].transactions
plt_dt = ut.transactions_to_dataframe(txs)
plt_dt["quantity"] = -plt_dt["quantity"]
plt_dt.loc[-1] = [0, i_px_init, 0]
plt_dt.sort_index(inplace=True)
plt_dt["quantity_cs"] = plt_dt["quantity"].cumsum()


def delta_scatter(prices, point_per_unit: int):
    px_min = math.floor(min(prices) - 0.1)
    px_max = math.ceil(max(prices) + 0.1)
    nb_points = (px_max - px_min) * point_per_unit + 1
    width = (px_max - px_min) / (nb_points - 1)

    xs = []
    ys = []
    for i in range(nb_points):
        x = px_min + i * width
        xs.append(x)
        ys.append(-delta_fun(x, 1) + delta_fun(i_px_init, 1))
    return (xs, ys)


delta_x, delta_y = delta_scatter(plt_dt["price"], 2)

fig = go.Figure()
fig.add_trace(
    go.Line(x=delta_x, y=delta_y, name="delta", mode="lines", line_color="lightblue"),
)
fig.add_trace(
    go.Scatter(
        x=plt_dt["price"],
        y=plt_dt["quantity_cs"],
        marker={"color": plt_dt["time"], "colorscale": "rainbow", "size": 5},
        name="maker delta",
        line_shape="vh",
        line_color="grey",
        line_width=1,
    ),
)
tabMakerAssets.plotly_chart(fig, use_container_width=True)


## TAB MONTE CARLO

st_loc = tabMC

col1up, col2up, _, col4 = st_loc.columns([1, 1, 1, 1])

# https://blog.streamlit.io/how-to-build-a-real-time-live-dashboard-with-streamlit/#4-how-to-refresh-the-dashboard-for-real-time-or-live-data-feed

# wrap arbitrage logic
sMonteCarlo = "monte_carlo"
state_get(sMonteCarlo, [])


def monte_carlo_one(resStore: List):

    maker = build_maker(use_latest_price=False)
    exchange = ExchangeSingleMaker(maker)

    path = simulate_path()
    time = 0
    dt = i_time_delta
    for price in path:
        time += dt
        exchange.apply_arbitrage(price, time)

    resStore.append(
        [
            state_context_repr(),
            path[-1],
            exchange.maker.cash,
            exchange.maker.asset,
            len(exchange.transactions),
        ]
    )


def monte_carlo_n(nbSim: int):
    resStore = state_get(sMonteCarlo)

    for i in range(nbSim):
        monte_carlo_one(resStore)


sMonteCarloCancel = "monte_carlo_cancel"

placeholder = tabMC.empty()


def display_monte_carlo():
    sims = pd.DataFrame(
        state_get(sMonteCarlo), columns=["maker", "price", "cash", "asset", "nb_tx"]
    )
    sims["pnl"] = sims["price"] * sims["asset"] + sims["cash"]

    with placeholder.container():

        fig = px.scatter(sims, x="price", y="asset", color="maker").add_hline(y=0)
        st.plotly_chart(fig, use_container_width=True)

        # plotting E[ pnl_T | price_T ]
        fig = px.scatter(sims, x="price", y="pnl", color="maker").add_hline(y=0)
        st.plotly_chart(fig, use_container_width=True)


if col2up.button("Stop Simulations"):
    state_set(sMonteCarloCancel, True)
else:
    state_set(sMonteCarloCancel, False)

if col1up.button("Start Simulations..."):

    state_set(sMonteCarloCancel, False)

    while not state_get(sMonteCarloCancel, False):

        monte_carlo_n(10)

        display_monte_carlo()

with placeholder.container():
    display_monte_carlo()

if col4.button("Reset Simulations"):
    state_set(sMonteCarlo, [])
    display_monte_carlo()
