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
        execute_query(""" 
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(1000) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            department VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            seniority VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            salary_min INTEGER NOT NULL,
            salary_max INTEGER NOT NULL,
            currency VARCHAR(10) NOT NULL,
            required_skills TEXT[] NOT NULL,
            nice_to_have_skills TEXT[] NOT NULL,
            dei_score INTEGER NOT NULL,
            applicant_count INTEGER DEFAULT 0,
            shortlisted_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            posted_url VARCHAR(255) NOT NULL,
            hiring_manager VARCHAR(255) NOT NULL
        );
        
        """)
        pg_connection.close()

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
