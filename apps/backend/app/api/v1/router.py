from fastapi import FastAPI
from api.v1.routes import candidates
from api.v1.routes import auth

v1_app = FastAPI(title="NeuroHire API v1", version="1.0.0")


v1_app.include_router(candidates.router)
print("Included candidates router")
v1_app.include_router(auth.router)
print("Included auth router")
