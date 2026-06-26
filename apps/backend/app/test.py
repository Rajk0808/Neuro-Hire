import asyncio
from services.pg_db_service import execute_query

async def main():
    # 1. Clean up existing tables
    await execute_query("DROP TABLE IF EXISTS users")
    
    # 2. Create the table structure
    await execute_query(
        "CREATE TABLE users (id SERIAL PRIMARY KEY, company_name VARCHAR(255), email VARCHAR(255) UNIQUE, password VARCHAR(255))"
    )
    
    # 3. Insert a record (Changed %s to $1, $2, $3)
    await execute_query(
        "INSERT INTO users (company_name, email, password) VALUES ($1, $2, $3)", 
        ("Test Company", "test@example.com", "hashed_password")
    )
    
    # 4. Query the record (Changed %s to $1 and added a trailing comma to make it a true tuple)
    res = await execute_query(
        "SELECT * FROM users WHERE email = $1", 
        ("test@example.com",)  # <--- Note the crucial trailing comma!
    )
    print(res[0])

if __name__ == "__main__":
    asyncio.run(main())
