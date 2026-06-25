from services.pg_db_service import execute_query
import asyncio
async def main():
    await execute_query("DROP TABLE IF EXISTS users")
    await execute_query("CREATE TABLE users (id SERIAL PRIMARY KEY, company_name VARCHAR(255), email VARCHAR(255) UNIQUE, password VARCHAR(255))")
    await execute_query("INSERT INTO users (company_name, email, password) VALUES (%s, %s, %s)", ("Test Company", "test@example.com", "hashed_password"))
    res = await execute_query("SELECT * FROM users WHERE email = %s", ("test@example.com"))
    print(res)

asyncio.run(main())