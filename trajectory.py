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


def clear_state_maker():
    del st.session_state["maker"]


numOffers = st.slider(
    "Number of offers (one way)", 1, 10, 3, on_change=clear_state_maker
)


tickInterval = st.number_input(
    "Tick interval to post offers", 0.25, 10.0, 2.0, 0.25, on_change=clear_state_maker
)

mat_float = float(nb_day) * float(mat_ratio) / float(NB_DAY_PER_YEAR)

if "maker" not in st.session_state:
    maker = MakerDelta(
        initMidPrice=px_init,
        deltaFunction=lambda x: -delta_fun(x, mat_float),
        numOneWayOffers=numOffers,
        tickInterval=tickInterval,
        tickQuantity=None,
    )
    st.session_state["maker"] = maker
    st.session_state["exchange"] = ExchangeSingleMaker(maker=maker)


# offers_dt =
st.table(ut.offers_to_dataframe(st.session_state["maker"].offers))

# fig_ob = px.bar(offers_dt, x="quantity", y="price", color="way", orientation="h")
# st.plotly_chart(fig_ob, use_container_width=True)


def set_counters(time_index: int):
    time_idx_cur = time_index
    time_idx_nxt = min(time_idx_cur + 1, len(prices))

    px_cur = prices[time_index]
    px_nxt = prices[time_idx_nxt]

    st.session_state["time_idx_cur"] = time_idx_cur
    st.session_state["time_idx_nxt"] = time_idx_nxt
    st.session_state["px_cur"] = px_cur
    st.session_state["px_nxt"] = px_nxt


if "time_idx_cur" not in st.session_state:
    set_counters(0)

if st.checkbox("Override next price"):
    st.session_state["px_nxt"] = st.number_input(
        "Override next price", 50.0, 200.0, st.session_state["px_cur"]
    )

delta_cur = st.session_state["maker"].computeDelta(st.session_state["px_cur"])
delta_nxt = st.session_state["maker"].computeDelta(st.session_state["px_nxt"])

# https://docs.streamlit.io/library/api-reference/data/st.metric
col1, col2 = st.columns(2)
col1.metric("Current Price", "%.2f" % st.session_state["px_cur"])
col2.metric("Current Delta", "%.2f" % delta_cur)
col1.metric(
    "Next Price",
    "%.2f" % st.session_state["px_nxt"],
    "%.4f" % (st.session_state["px_nxt"] - st.session_state["px_cur"]),
)
col2.metric("Next Delta", "%.2f" % delta_nxt, "%.4f" % (delta_nxt - delta_cur))

if st.button("Arb next Observation"):
    st.session_state["exchange"].apply_arbitrage(
        price=st.session_state["px_nxt"],
        time=float(st.session_state["time_idx_nxt"]) * time_delta,
    )
    set_counters(st.session_state["time_idx_nxt"])
    # breakpoint()

st.write(st.session_state)

st.write(st.session_state["exchange"].transactions)
