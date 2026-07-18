import asyncio
import json
from services.pg_db_service import execute_query

# 1. Wrap your code inside an async function
async def main():
    user_id = "user@email.com"
    raw_input = "This is a sample job description."
    
    # 2. Add the 'await' keyword here
    res = await execute_query(
        "INSERT INTO sessions (user_id, status, raw_draft) VALUES ($1, 'queued', $2)",
        (user_id, raw_input)
    )
    
    # 3. Pretty print the structured dictionary data
    print(json.dumps(res, indent=4, default=str))

# 4. Use asyncio to run the async main block
if __name__ == "__main__":
    asyncio.run(main())
