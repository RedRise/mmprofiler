from math import sqrt
import numpy as np
from numpy.random import default_rng


def geom_brownian_path(
    initPrice,
    yearlyDrift,
    yearlyVolat,
    numDaysToSimul,
    numStepPerDay: int = 1,
    numDaysPerYearConvention: int = 252,
):

    if initPrice < 0:
        raise ValueError("initPrice should be positive.")

    # initPrice = 100
    # yearlyDrift=0.1
    # yearlyVolat = 0.4
    # numDaysToSimul = 2000
    # numStepPerDay = 1
    # numDaysPerYearConvention = 252

    dt = 1 / float(numDaysPerYearConvention * numStepPerDay)
    numSimul = numDaysToSimul * numStepPerDay

    rng = default_rng()

    e = rng.normal(0, 1, int(numSimul))

    exponent = (yearlyDrift - 0.5 * yearlyVolat**2) * dt + yearlyVolat * sqrt(dt) * e
    exponent[0] = 0

    return initPrice * np.exp(np.cumsum(exponent))
