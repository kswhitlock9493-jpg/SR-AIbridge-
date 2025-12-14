#!/usr/bin/env python3
import math, time, json, sqlite3
from flask import Flask, request, jsonify
import serial, adafruit_dht, board

HARMONY_THRESHOLD = 0.9995
weights = [0.25, 0.20, 0.20, 0.15, 0.10, 0.10]

def calculate_mu(scores):
    scores = [max(min(s,1.0),1e-12) for s in scores]
    return math.exp(sum(w*math.log(s) for w,s in zip(weights,scores)))

def check_ch():
    return (not chemical_overdue()           and
            fume_hood_velocity_ok()         and
            biosafety_cert_valid()          and
            laser_interlock_ok()            and
            radiation_badge_current()       and
            irb_approval_valid()            and
            emergency_stop_not_pressed())

app = Flask(__name__)

@app.route("/resonance", methods=["GET"])
def resonance_gate():
    scores = [
        query_chemical_inventory_accuracy(),
        query_fume_hood_velocity(),
        query_biosafety_containment(),
        query_laser_interlock(),
        query_radiation_monitor(),
        query_student_training_score()
    ]
    mu = calculate_mu(scores)
    ch = check_ch()
    if mu >= HARMONY_THRESHOLD and ch:
        return jsonify({"status": "LAB GO", "mu": mu, "ch": ch})
    else:
        return jsonify({"status": "LAB HALT", "mu": mu, "ch": ch}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
