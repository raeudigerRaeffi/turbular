import requests
import json
import os
from typing import Dict, Any

def get_env_var(name: str, default: str) -> str:
    return os.environ.get(name, default)

def test_connection():
    # Connection details from environment variables
    connection_info = {
        "database_type": "PostgreSQL",
        "username": get_env_var("TEST_DB_USER", "postgres"),
        "password": get_env_var("TEST_DB_PASSWORD", "testpassword"),
        "host": get_env_var("TEST_DB_HOST", "localhost"),
        "port": int(get_env_var("TEST_DB_PORT", "5432")),
        "database_name": get_env_var("TEST_DB_NAME", "testdb"),
        "ssl": False
    }

    # Test endpoints
    base_url = "http://localhost:8000"
    
    # Test 1: Get schema
    print("\nTesting schema retrieval...")
    schema_response = requests.post(
        f"{base_url}/get_schema",
        json=connection_info
    )
    print_response("Schema", schema_response)

    # Test 2: Execute a simple query
    print("\nTesting query execution...")
    payload = {
    "db_info": connection_info,
    "query": "SELECT * FROM order_summaries LIMIT 3",
    "normalized_query": False,
    "max_rows": 3,
    "autocommit": True
}

    # Send it all as JSON in the request body
    query_response = requests.post(
        f"{base_url}/execute_query",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    print_response("Query", query_response)

def print_response(test_name: str, response: requests.Response):
    print(f"{test_name} Status Code:", response.status_code)
    if response.status_code == 200:
        print(f"{test_name} Response:", json.dumps(response.json(), indent=2))
    else:
        print(f"{test_name} Error:", response.text)

if __name__ == "__main__":
    test_connection() 