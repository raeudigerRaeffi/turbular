# Turbular API Documentation

This document provides detailed information about the Turbular API endpoints, their parameters, and response formats.

## Base URL

The API base URL depends on your deployment:
- Development: `http://localhost:8000`
- Production: Your deployed instance URL

## Authentication

Currently, the API does not require authentication. However, database credentials are required for each connection.

## Endpoints

### Database Schema

#### Get Database Schema

```http
POST /get_schema
```

Retrieves the schema of a connected database. Can return both native and normalized schemas.

**Request Body:**
```json
{
  "database_type": "PostgreSQL",
  "username": "user",
  "password": "password",
  "host": "localhost",
  "port": 5432,
  "database_name": "mydb",
  "ssl": false
}
```

**Optional Parameters:**
- `return_normalize_schema` (boolean): Return schema in LLM-friendly format

**Response:**
```json
{
  "database_schema": "string",
  "extraction_time": 0.123,
  "normalized_schema": "string"
}
```

### Query Execution

#### Execute Query

```http
POST /execute_query
```

Executes SQL queries on the connected database.

**Request Body:**
```json
{
  "db_info": {
    "database_type": "PostgreSQL",
    "username": "user",
    "password": "password",
    "host": "localhost",
    "port": 5432,
    "database_name": "mydb",
    "ssl": false
  },
  "query": "SELECT * FROM users LIMIT 10",
  "normalized_query": false,
  "max_rows": 10,
  "autocommit": true
}
```

**Response:**
```json
{
  "execution_time": 0.123,
  "query_result": {
    "columns": ["id", "name", "email"],
    "rows": [
      [1, "John Doe", "john@example.com"]
    ]
  },
  "executed_query": "SELECT * FROM users LIMIT 10"
}
```

### File Management

#### Upload BigQuery Key

```http
POST /upload-bigquery-key
```

Uploads a BigQuery service account key file.

**Form Data:**
- `project_id`: BigQuery project ID
- `key_file`: JSON key file

**Response:**
```json
{
  "message": "Successfully uploaded BigQuery key for project my-project"
}
```

#### List BigQuery Projects

```http
GET /bigquery-projects
```

Lists all available BigQuery projects.

**Response:**
```json
{
  "projects": ["project1", "project2"]
}
```

#### Upload SQLite Database

```http
POST /upload-sqlite-file
```

Uploads a SQLite database file.

**Form Data:**
- `database_name`: Name to identify the database
- `db_file`: SQLite database file (.db or .sqlite)

**Response:**
```json
{
  "message": "Successfully uploaded SQLite database my-database"
}
```

#### List SQLite Databases

```http
GET /sqlite-databases
```

Lists all available SQLite databases.

**Response:**
```json
{
  "databases": ["db1", "db2"]
}
```

### Utility Endpoints

#### Health Check

```http
GET /health
```

Verifies if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

#### List Supported Databases

```http
GET /supported-databases
```

Returns a list of all supported database types.

**Response:**
```json
[
  "PostgreSQL",
  "MySQL",
  "SQLite",
  "BigQuery",
  "Oracle",
  "MsSql",
  "Redshift"
]
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 201: Created (for successful uploads)
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Error responses include detailed messages:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, there are no rate limits implemented. However, consider the following best practices:

- Limit query result sizes using `max_rows`
- Implement appropriate timeouts in your client
- Consider caching frequently used schemas

## Best Practices

1. **Connection Management:**
   - Close connections when done
   - Use connection pooling for frequent queries
   - Implement retry logic in your client

2. **Query Optimization:**
   - Use `max_rows` to limit large result sets
   - Consider using normalized queries for LLM interactions
   - Test queries with small result sets first

3. **Security:**
   - Never expose database credentials
   - Use SSL when available
   - Implement proper access controls

4. **Error Handling:**
   - Implement proper error handling in your client
   - Log failed queries for debugging
   - Handle timeouts appropriately

## Examples

### Python Client Example

```python
import requests

def query_database(connection_info, query):
    response = requests.post(
        "http://localhost:8000/execute_query",
        json={
            "db_info": connection_info,
            "query": query,
            "normalized_query": False,
            "max_rows": 1000,
            "autocommit": True
        }
    )
    return response.json()

# Example usage
connection_info = {
    "database_type": "PostgreSQL",
    "username": "user",
    "password": "password",
    "host": "localhost",
    "port": 5432,
    "database_name": "mydb",
    "ssl": False
}

result = query_database(connection_info, "SELECT * FROM users LIMIT 10")
print(result)
```

## Support

For API support:
- Create an issue on GitHub
- Join our Discord community
- Email: support@turbular.dev 