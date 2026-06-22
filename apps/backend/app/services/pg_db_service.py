from db.session import get_pg_connection

def execute_query(query, params=None):
    connection = get_pg_connection()
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
        