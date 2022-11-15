import streamlit as st
from simul.path_generators import geom_brownian_path
from makers.maker_delta import MakerDelta
import utils as ut
import utils_black_scholes as bs
import plotly.express as px
from exchange_single_maker import ExchangeSingleMaker

NB_DAY_PER_YEAR = 252

st.title("Trajectory Viz")


st.header("Simulation parameters")
nb_day = st.slider("Nb simulated days", 0, 750, 252)
nb_step_day = st.slider("Nb intraday simulations", 0, 10, 1)
px_init = st.number_input("Initial price", 50.0, 200.0, 100.0)
return_y = st.slider("Yearly return (%)", -10, 50, 10) / 100
volat_y = st.slider("Yearly volatility (%)", 1, 80, 20) / 100
seed = st.number_input("Seed for diffusion", 0, None, 123)

time_delta = 1 / (float(NB_DAY_PER_YEAR) * float(nb_step_day))

prices = geom_brownian_path(
    px_init, return_y, volat_y, nb_day, nb_step_day, NB_DAY_PER_YEAR, seed
)

# st.line_chart(x=range(len(prices)), y=prices)
st.line_chart(prices)

st.header("Maker strategy")


def call_module():
    mat_ratio = (
        st.slider(
            "Maturity ratio w.r.t the number of simulated days (%)",
            0,
            100,
            100,
            step=25,
        )
        / 100
    )
    strike = st.slider("Option strike", 10, 200, 100, step=10)
    volat = st.slider("Volatility used for replication (%)", 1, 80, 20) / 100
    rate = st.slider("Rate used for replication (%)", -2, 20, 0) / 100
    return (mat_ratio, strike, volat, rate)


st.subheader("Call option parameters")
(mat_ratio, strike, volat_repli, rate_repli) = call_module()


def delta_fun(x: float, t: float) -> float:
    return bs.delta(x, strike, t, rate_repli, volat_repli)


# breakpoint()
char_prices = list(range(50, 150))
char_deltas = [delta_fun(x, 1.0) for x in char_prices]
fig = px.line(x=char_prices, y=char_deltas)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Market Making parameters")


# State

sExchange = "exchange"
sTimeIdx = "time_index"
sTime = "time"
sTimeIdxNxt = "time_idx_nxt"
sTimeOver = "time_over"
sPxCur = "px_cur"
sPxNxt = "px_nxt"
sDltCur = "delta_cur"
sDltNxt = "delta_nxt"

# maker (delta function) / exchange


def state_reset_maker():
    st.session_state[sExchange].maker = None


numOffers = st.slider(
    "Number of offers (one way)", 1, 10, 3,
    on_change=state_reset_maker
)


tickInterval = st.number_input(
    "Tick interval to post offers", 0.25, 10.0, 2.0, 0.25,
    on_change=state_reset_maker
)


def build_maker():
    p0 = st.session_state.get(sPxCur, px_init)

    mat_float = float(nb_day) * float(mat_ratio) / float(NB_DAY_PER_YEAR)
    maker = MakerDelta(
        initMidPrice=p0,
        deltaFunction=lambda x: -delta_fun(x, mat_float),
        numOneWayOffers=numOffers,
        tickInterval=tickInterval,
        tickQuantity=None,
    )
    return maker


def init_exchange():
    maker = build_maker()
    st.session_state[sExchange] = ExchangeSingleMaker(maker)


if sExchange not in st.session_state:
    init_exchange()

if not st.session_state[sExchange].maker:
    st.session_state[sExchange].maker = build_maker()


def update_state_time_idx():
    i = st.session_state[sTimeIdx]
    stss = st.session_state
    stss[sPxCur] = prices[i]
    time_idx_next = i + 1 if not stss[sTimeOver] else i
    stss[sTimeIdxNxt] = time_idx_next
    stss[sPxNxt] = prices[time_idx_next]

    maker = st.session_state[sExchange].maker
    stss[sDltCur] = maker.computeDelta(stss[sPxCur])
    stss[sDltNxt] = maker.computeDelta(stss[sPxNxt])


def time_clock():
    if not sTimeIdx in st.session_state:
        st.session_state[sTimeIdx] = 0
        st.session_state[sTimeOver] = False
        update_state_time_idx()
    else:
        time_idx = min(st.session_state[sTimeIdx] + 1, len(prices))
        st.session_state[sTimeIdx] = time_idx
        st.session_state[sTimeOver] = (time_idx >= len(prices))


# offers_dt =
st.table(ut.offers_to_dataframe(st.session_state[sExchange].offers))


# if "time_idx_cur" not in st.session_state:
#     set_counters(0)
time_clock()


# https://docs.streamlit.io/library/api-reference/data/st.metric
col1, col2 = st.columns(2)
col1.metric("Current Price", "%.2f" % st.session_state[sPxCur])
col2.metric("Current Delta", "%.2f" % st.session_state[sDltCur])
col1.metric(
    "Next Price",
    "%.2f" % st.session_state[sPxNxt],
    "%.4f" % (st.session_state[sPxNxt] - st.session_state[sPxCur]),
)
col2.metric("Next Delta", "%.2f" % st.session_state[sDltNxt], "%.4f" % (
    st.session_state[sDltNxt] - st.session_state[sDltCur]))

if st.button("Arb next Observation"):
    st.session_state["exchange"].apply_arbitrage(
        price=st.session_state[sPxNxt],
        time=float(st.session_state[sTimeIdxNxt]) * time_delta,
    )
    # set_counters(st.session_state["time_idx_nxt"])
    time_clock()
    update_state_time_idx()

st.write(st.session_state)

st.write(st.session_state["exchange"].transactions)

# https://plotly.com/python/line-charts/#interpolation-with-line-plots
