import os
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection = sql.connect(
        server_hostname=os.getenv("DATABRICKS_HOST"),
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN")
    )
    return connection


def run_query(query: str) -> list:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    connection.close()
    return columns, result


def test_connection():
    try:
        columns, result = run_query("SHOW TABLES IN retail_agent")
        print("Connection successful!")
        print("Tables found:")
        for row in result:
            print(f"  - {row[1]}")
    except Exception as e:
        print(f"Connection failed: {str(e)}")


if __name__ == '__main__':
    test_connection()