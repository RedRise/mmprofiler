from plotly.subplots import make_subplots
import math
from typing import List
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import utils as ut
import utils_black_scholes as bs
from exchange_single_maker import ExchangeSingleMaker
from makers.maker_delta import MakerDelta
from makers.maker_replication import MakerReplication
from models.transaction import Transaction
from simul.path_generators import geom_brownian_path
from sklearn.preprocessing import KBinsDiscretizer
from mlinsights.mlmodel import PiecewiseRegressor

# CONSTANTS -------------------------------------------------------------------

NB_DAY_PER_YEAR = 252

# STREAMLIT CONFIG ------------------------------------------------------------

st.set_page_config(layout="wide")

# DATA CONTAINER --------------------------------------------------------------


def exc_snap(time, bbid, bask, price, assets, delta_theo):
    return {
        "time": time,
        "bbid": bbid,
        "bask": bask,
        "price": price,
        "assets": assets,
        "delta_theo": delta_theo,
    }


# STREAMLIT STATE -------------------------------------------------------------

# State Variable Names

sExc = "exchange"
sExcSnapshots = "exchange_snapshots"
sTimeIdx = "time_index"
sTime = "time"
sTimeIdxNxt = "time_index_nxt"
sTimeOver = "time_over"
sPxCur = "px_cur"
sPxNxt = "px_nxt"
sDltCur = "delta_cur"
sDltNxt = "delta_nxt"
sRebuildMaker = "rebuild_maker"
sMonteCarlo = "monte_carlo"
sMonteCarloCancel = "monte_carlo_cancel"


# functions (getter/setter)


@st.experimental_memo
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


def state_set(varName: str, value):
    st.session_state[varName] = value


def state_get(varName: str, default_value=None):
    if varName not in st.session_state:
        state_set(varName, default_value)
    return st.session_state[varName]


def state_context_repr():
    return "μ:{:.0f} σs:{:.0f}, {} K:{} σr:{:.0f}, {} x {}".format(
        100 * i_yield,
        100 * i_volat,
        "D" if i_maker_repli else "S",
        i_strike,
        100 * i_volat_repli,
        i_nb_offers,
        i_tick_width,
    )


def state_maker_to_rebuild():
    state_set(sRebuildMaker, True)


# STREAMLIT LAYOUT ------------------------------------------------------------

st.markdown(
    "# Market Making with curves &emsp;[![Star](https://img.shields.io/github/stars/redrise/mmprofiler.svg?logo=github&style=social)](https://github.com/RedRise/mmprofiler)",
    unsafe_allow_html=True,
)


tabHome, tabTraj, tabCallOption, tabMaker, tabMC = st.tabs(
    ["🏠 Home", "📈 Single Path", "💸 Call Option", "🔨 Maker", "🎲 Monte Carlo"]
)

# TAB Home ---------------------------

text = """This app illustrates a market making activity based on a *curve* that
represents, for the maker, the target position of (base) tokens depending on
it's price. This application will be focused on a specific set of curves based
on the call option delta (in the Black and Scholes model). This delta curve
expresses the derivative of the call price, with respect to the underlying
token.

A distinction will be made between static and dynamic curves."""

tabHome.markdown(text)


col1, col2 = tabHome.columns(2)

col1.subheader("Static Curves")
text = """When a maker animates liquidity with a static curve, this is
very close to supply liquidity on a CF-AMM (constant function AMM). This app
allows to play with call option delta curves (for a fixed maturity), but same
experiment can be done with any decreasing curve."""
col1.markdown(text)


col2.subheader("Dynamic Curves")
text = """Dynamic curves make sense to illustrate options replication.
When buying a call option, you can offset it's small price variations by selling
a quantity of tokens (equals to it's delta). This delta depends on the token
price and the time to maturity that decreases over time (this is why we say that
the delta curve w.r.t. price is dynamic)"""
col2.markdown(text)

col1, _, col2 = tabHome.columns([4, 1, 4])
stStaticDeltaPlaceHolder = col1.empty()
stDynamicDeltaPlaceHolder = col2.empty()

# TAB TRAJ ---------------------------

st_loc = tabTraj

st_exp = st_loc.expander("Details", True)

st_exp.markdown(
    r"""
The trajectory is simulated as a geometric Brownian Motion. A basic model
assuming that the asset log-returns of the token price (St) follow a gaussian
distribution. (Wt) is the standard Brownian Motion. A closed formula (right
side) can be derived from this equation (left side).
This is called the **Black & Scholes model**.
"""
)

col1, col2 = st_exp.columns(2)
col1.latex(r"""\frac{dS_t}{S_t} = \mu dt + \sigma dW_t""")
col2.latex(r"""S_t = S_0 \times e^{(\mu - \frac{\sigma^2}{2})  t + \sigma  W_t }""")


st_loc.subheader("Simulation parameters")

col1up, _, col2up = st_loc.columns([4, 1, 4])

i_nb_day = col1up.slider("Nb simulated days", 0, 750, 252)
i_nb_step_day = col1up.slider("Nb intraday simulations", 0, 10, 1)
i_seed = col1up.number_input("Seed for diffusion", 0, None, 123)

i_yield = col2up.slider("Yearly return (%, μ)", -10, 50, 10) / 100
i_volat = col2up.slider("Yearly volatility (%, σ)", 1, 80, 20) / 100
i_px_init = col2up.number_input("Initial price (S_0)", 50.0, 200.0, 100.0, step=1.0)

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


# TAB CALL OPTION --------------------

st_loc = tabCallOption

st_exp = st_loc.expander("Details", True)

col1, col2 = st_exp.columns(2)

col1.markdown(
    r"""
This section describes the target call option to take delta function from. To be
more precise, the market making activity will be to hedge a long call position,
i.e. we will target - delta position of risky asset.

When using the Black & Scholes model, [closed
formulas](https://www.macroption.com/black-scholes-formula/) can be computed for
the price of the price (noted Π(Call)) and it's derivative with respect to the
token price St (noted Δ(Call)).

N is the cumulative distribution function
([cdf](https://en.wikipedia.org/wiki/Cumulative_distribution_function)) of the
[standard gaussian](https://en.wikipedia.org/wiki/Normal_distribution) random
variable.
"""
)

col2.latex(
    r"""
\begin{align*}
    d_1 & = \frac{ln(S_0/K) + (r + \sigma^2/2)T}{\sigma \sqrt{t}} \\[2.0ex]
    \Pi(Call_T^K) &  = S_0 N(d_1)  - K e^{-rT} N(d_1 - \sigma \sqrt{t}) \\[2.0ex]
    \Delta(Call_T^K) & = N(d_1)
\end{align*}
"""
)

col1up, colMid, col2up = st_loc.columns([4, 1, 4])

col1up.subheader("Parameters")
stCallPricePlaceholder = col2up.empty()

col1up, colMid, col2up = st_loc.columns([4, 1, 4])

i_mat_ratio = (
    col1up.slider(
        "Maturity ratio w.r.t the number of simulated days (%, T)",
        100,
        200,
        100,
        step=25,
    )
    / 100
)
i_strike = col1up.slider(
    "Strike (K)",
    math.floor(0.10 * i_px_init),
    math.ceil(2 * i_px_init),
    int(i_px_init),
    step=10,
)
i_volat_repli = col2up.slider("Volatility used for replication (%, σ)", 1, 80, 20) / 100
i_rate_repli = col2up.slider("Rate used for replication (%, r)", -2, 20, 0) / 100

i_mat = float(i_mat_ratio) * float(i_nb_day) / float(NB_DAY_PER_YEAR)

i_call_price = bs.call_price(
    S=i_px_init, K=i_strike, r=i_rate_repli, sigma=i_volat_repli, T=i_mat
)
with stCallPricePlaceholder:
    text = "### Call Price : <mark>{:.2f}</mark>"
    st.markdown(text.format(i_call_price), unsafe_allow_html=True)


def delta_fun(x: float, t: float) -> float:
    return bs.call_delta(x, i_strike, t, i_rate_repli, i_volat_repli)


char_prices = list(range(math.floor(i_px_init * 0.5), math.ceil(1.5 * i_px_init)))
char_deltas = [delta_fun(x, i_mat) for x in char_prices]
fig = px.line(x=char_prices, y=char_deltas)
fig.update_layout(showlegend=False)

st_loc.subheader("Delta Function")
st_loc.plotly_chart(fig, use_container_width=True)
stStaticDeltaPlaceHolder.plotly_chart(fig, use_container_width=True)

char_time = list(range(1, i_nb_day, 10))
dlt3d_dt = pd.DataFrame(char_prices[::5], columns=["price"]).merge(
    pd.DataFrame(char_time, columns=["time"]), how="cross"
)
dlt3d_dt["time"] = dlt3d_dt["time"] / NB_DAY_PER_YEAR
dlt3d_dt["delta"] = dlt3d_dt.apply(lambda r: delta_fun(r["price"], r["time"]), axis=1)

dlt3d_dt = pd.pivot(dlt3d_dt, index="price", columns="time", values="delta")
fig = go.Figure(data=[go.Surface(z=dlt3d_dt, x=dlt3d_dt.index, y=char_time)])
fig.update_traces(showscale=False)
fig.update_scenes(
    xaxis_title_text="price",
    yaxis_title_text="time to maturity",
    zaxis_title_text="delta",
)
stDynamicDeltaPlaceHolder.plotly_chart(fig, use_container_width=True)

# TAB MAKER --------------------------

st_loc = tabMaker

_, col1up, _, col2up, _ = st_loc.columns([1, 2, 1, 3, 1])

col1up.subheader("Parameters")

i_maker_repli = col1up.checkbox("Use Dynamic Delta (vs. fixed curve)", True)

i_nb_offers = col1up.slider(
    "Number of offers (one way)", 1, 10, 2, on_change=state_maker_to_rebuild
)

i_tick_width = col1up.number_input(
    "Tick interval to post offers",
    0.25,
    10.0,
    1.0,
    0.25,
    on_change=state_maker_to_rebuild,
)


tabFrame, tabPlot = col2up.tabs(["DataFrame", "Chart"])
stMkTablePlaceholder = tabFrame.empty()
stMkPlotPlaceholder = tabPlot.empty()


def build_maker(use_latest_price: bool):
    if use_latest_price:
        p0 = st.session_state.get(sPxCur, i_px_init)
    else:
        p0 = i_px_init

    mat_float = float(i_nb_day) * float(i_mat_ratio) / float(NB_DAY_PER_YEAR)

    if i_maker_repli:
        maker = MakerReplication(
            initMidPrice=p0,
            deltaFunction=lambda x, t: -delta_fun(x, t),
            maturity=i_mat,
            numOneWayOffers=i_nb_offers,
            tickInterval=i_tick_width,
            tickQuantity=None,
        )
    else:
        maker = MakerDelta(
            initMidPrice=p0,
            deltaFunction=lambda x: -delta_fun(x, mat_float),
            numOneWayOffers=i_nb_offers,
            tickInterval=i_tick_width,
            tickQuantity=None,
        )
    return maker


def init_exchange():
    state_set(sExc, ExchangeSingleMaker(None))
    state_set(sRebuildMaker, True)
    state_set(sExcSnapshots, [])


def reset_maker_state():
    if sTimeIdx in st.session_state:
        del st.session_state[sTimeIdx]
    # state_maker_to_rebuild()
    init_exchange()
    update_state_time_idx()


if sExc not in st.session_state:
    init_exchange()


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
        st.session_state[sExc].maker = maker
        state_set(sRebuildMaker, False)

    maker = st.session_state[sExc].maker
    stss[sDltCur] = maker.computeDelta(stss[sPxCur])
    stss[sDltNxt] = maker.computeDelta(stss[sPxNxt])

    bbid = maker.offers.get_best_bid()
    bask = maker.offers.get_best_ask()
    state_get(sExcSnapshots).append(
        exc_snap(
            i * i_time_delta,
            bbid.price if bbid else None,
            bask.price if bask else None,
            stss[sPxCur],
            maker.asset,
            maker.computeDelta(stss[sPxCur]),
        )
    )


def time_clock():
    time_idx = min(st.session_state[sTimeIdx] + 1, len(i_prices))
    st.session_state[sTimeIdx] = time_idx
    st.session_state[sTimeOver] = time_idx >= len(i_prices)


def apply_arbitrage():
    px_nxt = state_get(sPxNxt)
    time_nxt = float(state_get(sTimeIdxNxt)) * i_time_delta

    exchange: ExchangeSingleMaker = state_get(sExc)
    exchange.apply_arbitrage(price=px_nxt, time=time_nxt)

    time_clock()
    update_state_time_idx()


def display_maker():
    offers_dt = ut.offers_to_dataframe(st.session_state[sExc].offers)
    with stMkTablePlaceholder:
        st.table(offers_dt)

    with stMkPlotPlaceholder:
        st.plotly_chart(
            px.bar(offers_dt, x="quantity", y="price", color="way", orientation="h"),
            use_container_width=True,
        )


update_state_time_idx()
display_maker()

st_loc.markdown("""---""")
col1up, col2up, _, col4 = st_loc.columns([1, 1, 1, 1])

if col1up.button("Go to next time step"):
    apply_arbitrage()
    display_maker()

if col2up.button("Go to end"):
    while state_get(sTimeIdx) < len(i_prices) - 2:
        apply_arbitrage()
    display_maker()

if col4.button("Reset"):
    reset_maker_state()
    display_maker()


# Metrics

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

tabMakerAssets, tabTxs, tabSnaps, tabDebug = st_loc.tabs(
    ["Maker assets", "Taker txs", "Snapshots", "[debug_state]"]
)

snaps_dt = pd.DataFrame(state_get(sExcSnapshots))

tabTxs.write(st.session_state["exchange"].transactions)
tabSnaps.table(snaps_dt)
tabDebug.write(st.session_state)

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
    go.Scatter(x=snaps_dt["time"], y=snaps_dt["price"], name="price"), secondary_y=False
)
fig.add_trace(
    go.Scatter(
        x=snaps_dt["time"], y=snaps_dt["bbid"], line_shape="hv", name="best bid"
    ),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(
        x=snaps_dt["time"], y=snaps_dt["bask"], line_shape="hv", name="best ask"
    ),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(
        x=[state_get(sTimeIdx) * i_time_delta, state_get(sTimeIdxNxt) * i_time_delta],
        y=[state_get(sPxCur), state_get(sPxNxt)],
        line=dict(dash="dash"),
        name="next price",
    ),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(
        x=snaps_dt["time"],
        y=snaps_dt["delta_theo"],
        name="delta theo",
        visible="legendonly",
    ),
    secondary_y=True,
)
fig.update_xaxes(title_text="Time (in year)")
fig["layout"]["yaxis2"]["showgrid"] = False
tabMakerAssets.plotly_chart(fig, use_container_width=True)

fig = px.scatter(
    snaps_dt,
    x="delta_theo",
    y="assets",
    # mode="markers",
    # name="asset vs. delta",
    trendline="ols",
    trendline_color_override="orange",
)
fig.update_xaxes(title_text="Target Delta")
fig.update_yaxes(title_text="Realized Delta")
tabMakerAssets.plotly_chart(fig, use_container_width=True)


# TAB MONTE CARLO ---------------------

st_loc = tabMC

col0, rightSide = st_loc.columns([4, 2])

i_add_call = rightSide.checkbox("Add Long Call Position")

i_detect_trend = rightSide.checkbox("Detect linear trends")


# https://blog.streamlit.io/how-to-build-a-real-time-live-dashboard-with-streamlit/#4-how-to-refresh-the-dashboard-for-real-time-or-live-data-feed
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


placeholder = col0.empty()


def get_x_range(df, column: str):
    return np.arange(df[column].min().round(), df[column].max().round())


def fit_and_predict(df, x):

    x = np.array(x).reshape(-1, 1)
    model = PiecewiseRegressor(verbose=True, binner=KBinsDiscretizer(n_bins=4))
    model.fit(
        df["price"].to_numpy().reshape(-1, 1), df["pnl"].to_numpy().reshape(-1, 1)
    )
    return pd.DataFrame({"price": x[:, 0], "pnl": model.predict(x)}).reset_index()


def display_monte_carlo():
    sims = pd.DataFrame(
        state_get(sMonteCarlo), columns=["maker", "price", "cash", "asset", "nb_tx"]
    )
    sims["pnl"] = sims["price"] * sims["asset"] + sims["cash"]
    sims["call"] = (sims["price"] - i_strike).clip(0, None)

    with placeholder.container():

        fig = px.scatter(sims, x="price", y="asset", color="maker").add_hline(y=0)
        st.plotly_chart(fig, use_container_width=True)

        # plotting E[ pnl_T | price_T ]

        if i_add_call:
            sims["pnl"] += sims["call"]

        sims = sims[["price", "pnl", "maker"]]

        if i_detect_trend:
            x_range = get_x_range(sims, "price")
            fits = sims.groupby("maker").apply(lambda df: fit_and_predict(df, x_range))
            fits = fits.reset_index().drop(["index", "level_1"], axis=1)
            fits["maker"] = "(fit) " + fits["maker"]

            sims = pd.concat([sims, fits[["price", "pnl", "maker"]]])

        fig = px.scatter(sims, x="price", y="pnl", color="maker").add_hline(y=0)
        if i_add_call:
            fig.add_hline(y=i_call_price, name="call price", opacity=0.3)

        st.plotly_chart(fig, use_container_width=True)
        state_set("sims_csv", convert_df(sims))


if rightSide.button("Stop Simulations"):
    state_set(sMonteCarloCancel, True)
else:
    state_set(sMonteCarloCancel, False)

if rightSide.button("Start Simulations..."):

    state_set(sMonteCarloCancel, False)

    while not state_get(sMonteCarloCancel, False):

        monte_carlo_n(10)

        display_monte_carlo()

with placeholder.container():
    display_monte_carlo()


if rightSide.button("Reset Simulations"):
    state_set(sMonteCarlo, [])
    display_monte_carlo()

if state_get("sims_csv", None):
    rightSide.download_button(
        "Press to Download",
        state_get("sims_csv", None),
        "sims.csv",
        "text/csv",
        key="download-csv",
        # disabled=not sims_csv,
    )

rightSide.markdown(
    r"""
### Legend Syntax
- μ : token annual yield
- σs : token real volatility
- D/S : dynamic or static delta curve
- K : reference option strike
- σr : volatility used for replication (mm)
- n x d : number of offers x interval width
"""
)
