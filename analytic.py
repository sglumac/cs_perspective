import numpy as np  # pylint: disable=import-error
from typing import NamedTuple, Callable, Dict, Any
from fractions import Fraction
import matplotlib.pyplot as plt
    
    
def first_order_response(y0, yEnd, lmbda, ts):
    """Exponential"""
    return y0 + (yEnd - y0) * (1 - np.exp(lmbda * ts))


def solution(dt, tEnd, w_omega=1., w_alpha=1., d=10., J=10., stepAmp=1):
    """
    w_omega = parameters.engine.w_omega
    w_alpha = parameters.engine.w_alpha
    d = parameters.inertia.damping
    J = parameters.inertia.inertia
    stepAmp = 1
    """

    lmbda = - (d - w_omega) / J
    k = w_alpha*stepAmp/(d-w_omega)

    results = dict()
    t = 0.
    ts = [t]
    while t < tEnd:
        t += dt
        ts.append(t)
        
    results['step_size'] = dt
    omega2 = first_order_response(0, k, lmbda, 1)

    def omega_calc(t):
        if t < 1:
            return 0.
        elif t < 2:
            return first_order_response(0, k, lmbda, t - 1)
        else:
            return first_order_response(omega2, 0, lmbda, t - 2)

    omegas = [omega_calc(t) for t in ts]
    results['Inertia', 'velocity'] = omegas
    results['Engine', 'velocity'] = omegas
    taus = [
        w_omega * omega + w_alpha * (stepAmp if (t >= 1. and t < 2.) else 0.)
        for omega, t in zip(omegas, ts)
    ]
    results['Inertia', 'torque'] = taus
    results['Engine', 'torque'] = taus
    return results


if __name__ == "__main__":
    ts, omegas, _ = solution(1.,1.,10.,10.)
    plt.plot(ts, omegas)
    plt.show() 
