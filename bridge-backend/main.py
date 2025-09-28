from fastapi import FastAPI
from bridge_core.vault.routes import router as vault_router

app = FastAPI()
app.include_router(vault_router)