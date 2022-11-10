import streamlit as st
from simul.path_generators import geom_brownian_path

st.title("Trajectory Viz")

if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write([0, 1, 2])

st.header("Simulation parameters")
nb_day = st.slider("Nb simulated days", 0, 750, 252)
nb_step_day = st.slider("Nb intraday simulations", 0, 10, 1)
px_init = st.slider("Initial price", 50, 200, 100)
return_y = st.slider("Yearly return", -10, 50, 10) / 100
volat_y = st.slider("Yearly volatility", 1, 80, 20) / 100
seed = st.number_input("Seed for diffusion", 0, None, 123)

prices = geom_brownian_path(px_init, return_y, volat_y, nb_day, nb_step_day, 252, seed)

# st.line_chart(x=range(len(prices)), y=prices)
st.line_chart(prices)

# st.header("Maker strategy")

# MAKER_DELTA = "delta"
# MAKER_DYN_DELTA = "dynamic delta"

# makerType = st.selectbox(
#     "What maker do you want to test?", (MAKER_DELTA, MAKER_DYN_DELTA)
# )


# def call_module():
#     maturity_ratio = st.slider("Maturity ratio", 0, 100, 100, step=25)


# if makerType == MAKER_DELTA:
#     st.subheader(MAKER_DELTA)
#     call_module()


# if makerType == MAKER_DYN_DELTA:
#     st.subheader(MAKER_DYN_DELTA)
