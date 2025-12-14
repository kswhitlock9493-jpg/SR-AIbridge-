from fastapi import FastAPI
from modules.quantum_intention_calibrator.resonance_mapper import ResonanceMapper
from modules.quantum_intention_calibrator.probability_collapser import ProbabilityCollapser
import pathlib, json

app = FastAPI(title="QIC Daemon", version="0.1.0")
mapper, collapser = ResonanceMapper(), ProbabilityCollapser(pathlib.Path("."))

@app.post("/qic/intention")
def deploy_intention(body: dict):
    params  = mapper.intention_to_params(body["intention"])
    pathway = collapser.collapse(params)
    return {"resonance_params": params, "pathway": pathway}

@app.get("/qic/health")
def health():
    return {"status": "resonating", "frequency": 1440}
