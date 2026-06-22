from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import sys
sys.path.append(str(Path(__file__).parent))
from api import v1_app 
from contextlib import asynccontextmanager
from db.session import get_pg_connection
from services.pg_db_service import execute_query
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting up... Starting background service.")
    pg_connection = get_pg_connection()
    if pg_connection:
        print("Successfully connected to PostgreSQL.")
        pg_connection.close()
        execute_query("""     
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """)
    else:
        print("Failed to connect to PostgreSQL.")
    yield
    print("Application is shutting down... Stopping background service.")

app = FastAPI(title="NeuroHire API", version="1.0.0", lifespan=lifespan)

frontend_origins = os.getenv("FRONTEND_ORIGINS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/v1", v1_app)


@app.get("/")
def read_root():
    return {"message": "Welcome to the NeuroHire API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
