from fastapi import FastAPI, APIRouter
from api.v1.routes import candidates

v1_app = FastAPI(title="NeuroHire API v1", version="1.0.0")


v1_app.include_router(candidates.router)
