import asyncpg
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())

async def get_pg_connection()->asyncpg.Connection | None:
    try:
        connection = await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "neurohire"),
            user=os.getenv("POSTGRES_USER", "root"),
            password=os.getenv("POSTGRES_PASSWORD", "password")
        )
        return connection
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None
