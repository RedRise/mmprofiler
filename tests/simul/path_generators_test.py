from simul.path_generators import *
import numpy as np
from math import isclose

def test_geom_brownian_path():

    drift = 0.2
    volat = 0.4
    sim1 = geom_brownian_path(100, drift, volat, 1)
    assert len(sim1) == 1

    sim2 = geom_brownian_path(100, drift, volat, 2)
    assert len(sim2) == 2

    sim3 = geom_brownian_path(100, drift, volat, 1000000)
    mean_dlog = np.diff(np.log(sim3)).mean()
    assert isclose(mean_dlog, (drift - 0.5 * volat**2)/252.0, rel_tol=0.5)

    std_dlog = np.diff(np.log(sim3)).std()
    assert isclose(std_dlog, volat * sqrt(1/252.0), rel_tol=1e-2)