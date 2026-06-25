from db.session import get_pg_connection

async def execute_query(query, params=None):
    res = get_pg_connection()
    connection = res
    if connection is None:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return True
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        connection.close()
        