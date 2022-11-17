import numpy as np
from scipy.stats import norm


def call_delta(S: float, K: float, T: float, r: float, sigma: float) -> float:
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    # d2 = d1 - sigma * np.sqrt(T)
    return norm.cdf(d1, 0.0, 1)


def call_price(S: float, K: float, T: float, r: float, sigma: float):

    # S: spot price
    # K: strike price
    # T: time to maturity
    # r: interest rate
    # sigma: volatility of underlying asset

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

    price = S * norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * norm.cdf(d2, 0.0, 1.0)

    return price
