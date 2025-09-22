from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SR-AIbridge Backend")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Agents
@app.get("/agents", response_model=list[schemas.Agent])
def list_agents(db: Session = Depends(get_db)):
    return crud.get_agents(db)

@app.post("/agents", response_model=schemas.Agent)
def register_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    return crud.create_agent(db, agent)

# Doctrine Logs
@app.get("/doctrine", response_model=list[schemas.DoctrineLog])
def list_doctrine(db: Session = Depends(get_db)):
    return crud.get_doctrine(db)

@app.post("/doctrine", response_model=schemas.DoctrineLog)
def add_doctrine(log: schemas.DoctrineLogBase, db: Session = Depends(get_db)):
    return crud.create_doctrine(db, log)

# Mission Logs
@app.get("/missions", response_model=list[schemas.MissionLog])
def list_missions(db: Session = Depends(get_db)):
    return crud.get_missions(db)

@app.post("/missions", response_model=schemas.MissionLog)
def create_mission(mission: schemas.MissionLogBase, db: Session = Depends(get_db)):
    return crud.create_mission(db, mission)