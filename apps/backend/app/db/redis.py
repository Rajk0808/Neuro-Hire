from redis.asyncio import Redis, BlockingConnectionPool
import os 
from dotenv import load_dotenv

load_dotenv()

async def get_redis_connection():
    try:
        pool = await BlockingConnectionPool(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), max_connections=20, decode_responses=True)
        redis = await Redis(
            connection_pool=pool
        )
        return redis
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        return None