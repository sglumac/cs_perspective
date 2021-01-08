import numpy as np  # pylint: disable=import-error
from typing import NamedTuple, Callable, Dict, Any
from fractions import Fraction
    
    
def first_order_response(k, lmbda, ts):
    """Exponential"""
    return k * (1 - np.exp(lmbda * ts))


def analytic_step_solution(w_omega, w_alpha, d, J, stepAmp=1, start_time=0., end_time=10., freq = 1e-6):
    """analytic"""
    """w_omega = parameters.engine.w_omega
    w_alpha = parameters.engine.w_alpha
    d = parameters.inertia.damping
    J = parameters.inertia.inertia
    stepAmp = 1"""

    lmbda = - (d - w_omega) / J
    k = w_alpha*stepAmp/(d-w_omega)

    ts = np.linspace(start_time, end_time, 1/freq)
    omegas = [
        first_order_response(k, lmbda, t) 
        for t in ts
    ]
    taus = [
        w_omega * omega + w_alpha * stepAmp
        for omega, t in zip(omegas, ts)
    ]
    return ts, omegas, taus



