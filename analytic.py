import numpy as np  # pylint: disable=import-error
from typing import NamedTuple, Callable, Dict, Any
from fractions import Fraction
import matplotlib.pyplot as plt
    
    
def first_order_response(k, lmbda, ts):
    """Exponential"""
    return k * (1 - np.exp(lmbda * ts))


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
    omegas = [
        first_order_response(k, lmbda, t) 
        for t in ts
    ]
    results['Inertia', 'velocity'] = omegas
    results['Engine', 'velocity'] = omegas
    taus = [
        w_omega * omega + w_alpha * stepAmp
        for omega, t in zip(omegas, ts)
    ]
    results['Inertia', 'torque'] = taus
    results['Engine', 'torque'] = taus
    return results


if __name__ == "__main__":
    ts, omegas, _ = solution(1.,1.,10.,10.)
    plt.plot(ts, omegas)
    plt.show() 
