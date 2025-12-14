#!/usr/bin/env python3
import math, time, gridlabs

HARMONY_THRESHOLD = 0.9995
weights = [0.30, 0.25, 0.20, 0.15, 0.10]

def compute_mu(scores):
    scores = [max(min(s,1.0),1e-12) for s in scores]
    return math.exp(sum(w*math.log(s) for w,s in zip(weights,scores)))

def check_ch():
    return all([
        cyber_alarm_clear(),
        phase_angle_within_5deg(),
        freq_within_50mhz(),
        breaker_interlock_ok(),
        operator_override_off()
    ])

def loop():
    while True:
        scores = [query_gen_frequency_coherence(),
                  query_phase_angle_stability(),
                  query_hvdc_health(),
                  query_market_price_convergence(),
                  query_cyber_posture()]
        mu = compute_mu(scores)
        ch = check_ch()
        if mu >= HARMONY_THRESHOLD and ch:
            print("Grid: SWITCH GO")
        else:
            print("Grid: SWITCH HALT – hold breaker")
        time.sleep(0.02)   # 50 Hz
