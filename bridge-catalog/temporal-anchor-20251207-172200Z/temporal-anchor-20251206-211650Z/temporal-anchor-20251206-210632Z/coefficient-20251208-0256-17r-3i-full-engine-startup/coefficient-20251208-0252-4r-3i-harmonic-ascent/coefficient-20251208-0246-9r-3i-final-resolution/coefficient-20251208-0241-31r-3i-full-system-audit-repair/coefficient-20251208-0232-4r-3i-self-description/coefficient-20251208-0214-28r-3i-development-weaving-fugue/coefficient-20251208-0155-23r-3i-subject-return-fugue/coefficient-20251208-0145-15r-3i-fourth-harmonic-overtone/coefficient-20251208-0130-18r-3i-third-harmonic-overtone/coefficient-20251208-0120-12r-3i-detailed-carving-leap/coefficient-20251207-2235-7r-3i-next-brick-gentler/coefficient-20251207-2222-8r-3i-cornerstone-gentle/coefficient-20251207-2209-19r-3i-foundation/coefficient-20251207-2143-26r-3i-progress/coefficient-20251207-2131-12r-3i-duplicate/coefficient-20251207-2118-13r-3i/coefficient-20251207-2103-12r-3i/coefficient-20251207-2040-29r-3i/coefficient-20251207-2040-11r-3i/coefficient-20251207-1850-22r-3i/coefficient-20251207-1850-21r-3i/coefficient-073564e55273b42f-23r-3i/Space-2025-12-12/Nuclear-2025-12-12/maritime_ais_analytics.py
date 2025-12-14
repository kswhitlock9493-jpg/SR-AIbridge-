#!/usr/bin/env python3
import math, time, pyais
from collections import deque

HARMONY_THRESHOLD = 0.9995
weights = [0.30, 0.25, 0.20, 0.15, 0.10]

def calculate_mu(scores):
    scores = [max(min(s,1.0),1e-12) for s in scores]
    return math.exp(sum(w*math.log(s) for w,s in zip(weights,scores)))

def check_ch():
    return (ais_spoof_score() > 0.95      and
            stability_index() >= 0.5      and
            engine_temp_ratio() < 0.9     and
            cargo_temp_deviation() < 2.0  and
            cyber_threat_score() > 0.95   and
            insurer_waiver_ok())

def loop():
    sock = pyais.AISStream(url="udp://0.0.0.0:4158")
    for msg in sock:
        scores = [
            ais_integrity_score(msg),
            engine_health_score(),
            stability_index(),
            cargo_temp_score(),
            cyber_score(),
            insurer_score()
        ]
        mu = calculate_mu(scores)
        ch = check_ch()
        if mu >= HARMONY_THRESHOLD and ch:
            print("Maritime: MANOEUVRE GO")
        else:
            print("Maritime: MANOEUVRE HALT – hold position")
        time.sleep(1) # 1 Hz
