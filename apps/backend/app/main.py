from fastapi import FastAPI
from apps.backend.app.middleware.cors import setup_cors
from middleware import Oauth2Middleware
from pathlib import Path
import os
import sys
sys.path.append(str(Path(__file__).parent))
from api import v1_app 
from contextlib import asynccontextmanager
from apps.backend.app.db.postgres import get_pg_connection
from services.pg_db_service import create_db
from db.redis import get_redis_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting up... Starting background service.")
    pg_connection = await get_pg_connection()
    redis_connection = await get_redis_connection()
    if pg_connection:
        print("Successfully connected to PostgreSQL.")
        res =  await create_db()
        if res:
            print("Database created successfully.")
        await pg_connection.close()
        await redis_connection.aclose()

    else:
        print("Failed to connect to PostgreSQL.")
    yield
    print("Application is shutting down... Stopping background service.")

app = FastAPI(title="NeuroHire API", version="1.0.0", lifespan=lifespan)

frontend_origins = os.getenv("FRONTEND_ORIGINS")

app.add_middleware(Oauth2Middleware)
setup_cors(app, frontend_origins.split(",") if frontend_origins else ["*"])
    
app.mount("/v1", v1_app)

@app.get("/")
def read_root():
    return {"message": "Welcome to the NeuroHire API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
