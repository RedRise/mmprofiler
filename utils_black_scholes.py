import numpy as np
from scipy.stats import norm


def delta(S: float, K: float, T: float, r: float, sigma: float) -> float:
    d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
    # d2 = d1 - sigma * np.sqrt(T)
    return norm.cdf(d1)
