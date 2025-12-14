#!/usr/bin/env python3
import math, time, obd

HARMONY_THRESHOLD = 0.9995
weights = [0.30, 0.25, 0.20, 0.15, 0.10]

def compute_mu(scores):
    scores = [max(min(s,1.0),1e-12) for s in scores]
    return math.exp(sum(w*math.log(s) for w,s in zip(weights,scores)))

def check_ch():
    return all([
        asil_d_fault_free(),
        torque_controllable(),
        velocity_delta_safe(),
        hands_on_wheel_or_l3(),
        obd_safety_dtc_clear()
    ])

def loop():
    connection = obd.OBD()
    while True:
        scores = [query_brake_health(connection),
                  query_perception_confidence(connection),
                  query_battery_health(connection),
                  query_steering_health(connection),
                  query_driver_monitor(connection)]
        mu = compute_mu(scores)
        ch = check_ch()
        if mu >= HARMONY_THRESHOLD and ch:
            print("Drive: RESONANCE GO")
        else:
            print("Drive: HALT — safe-state activated")
        time.sleep(0.1)

if __name__ == "__main__":
    loop()
