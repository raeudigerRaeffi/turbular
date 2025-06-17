[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/raeudigerraeffi-turbular-badge.png)](https://mseep.ai/app/raeudigerraeffi-turbular)

# Turbular 

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)](LICENSE)

</div>

Turbular is an open-source Model Context Protocol (MCP) server that enables seamless database connectivity for Language Models (LLMs). It provides a unified API interface to interact with various database types, making it perfect for AI applications that need to work with multiple data sources.

## ✨ Features

- 🔌 **Multi-Database Support**: Connect to various database types through a single API
- 🔄 **Schema Normalization**: Automatically normalize database schemas to correct naming conventions for LLM compatibility
- 🔒 **Secure Connections**: Support for SSL and various authentication methods
- 🚀 **High Performance**: Optimizes your LLM generated queries
- 📝 **Query Transformation**: Let LLM generate queries against normalized layouts and transform them into their unnormalized form
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose
- 🔧 **Easy to Extend**: Adding new database providers can be easily done by extending the [BaseDBConnector interface](app/data_oracle/connectors/baseconnector.py) 

## 🗄️ Supported Databases

| Database Type | Status |  Icon |
|--------------|--------|------|
| PostgreSQL   | ✅     |  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original.svg" width="20" height="20"> |
| MySQL        | ✅     |  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/mysql/mysql-original.svg" width="20" height="20"> |
| SQLite       | ✅     | <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/sqlite/sqlite-original.svg" width="20" height="20"> |
| BigQuery     | ✅     |  <img src="https://www.vectorlogo.zone/logos/google_bigquery/google_bigquery-icon.svg" width="20" height="20"> |
| Oracle       | ✅     |  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/oracle/oracle-original.svg" width="20" height="20"> |
| MS SQL       | ✅     |  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/microsoftsqlserver/microsoftsqlserver-plain.svg" width="20" height="20"> |
| Redshift     | ✅     |  <img src="https://cdn2.iconfinder.com/data/icons/amazon-aws-stencils/100/Database_copy_Amazon_RedShift-512.png" width="20" height="20"> |

## 🚀 Quick Start

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/raeudigerRaeffi/turbular.git
   cd turbular
   ```

2. Start the development environment:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. Test the connection:
   ```bash
   ./scripts/test_connection.py
   ```

### Manual Installation

1. Install Python 3.11 or higher

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## 🔌 API Reference

### Database Operations

#### Get Database Schema
```http
POST /get_schema
```
Retrieve the schema of a connected database for your LLM agent.

**Parameters:**
- `db_info`: Database connection arguments
- `return_normalize_schema` (optional): Return schema in LLM-friendly format

#### Execute Query
```http
POST /execute_query
```
Optimizes query and then execute SQL queries on the connected database.

**Parameters:**
- `db_info`: Database connection arguments
- `query`: SQL query string
- `normalized_query`: Boolean indicating if query is normalized
- `max_rows`: Maximum number of rows to return
- `autocommit`: Boolean for autocommit mode

### File Management

#### Upload BigQuery Key
```http
POST /upload-bigquery-key
```
Upload a BigQuery service account key file.

**Parameters:**
- `project_id`: BigQuery project ID
- `key_file`: JSON key file

#### Upload SQLite Database
```http
POST /upload-sqlite-file
```
Upload a SQLite database file.

**Parameters:**
- `database_name`: Name to identify the database
- `db_file`: SQLite database file (.db or .sqlite)

### Utility Endpoints

#### Health Check
```http
GET /health
```
Verify if the API is running.

#### List Supported Databases
```http
GET /supported-databases
```
Get a list of all supported database types.

## 🔧 Development Setup

1. Fork and clone the repository

2. Create a development environment:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

3. The development server includes:
   - FastAPI server with hot reload
   - PostgreSQL test database
   - Pre-configured test data

4. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc


## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Check out our [contribution guidelines](CONTRIBUTING.md)
2. Look for [open issues](https://github.com/raeudigerRaeffi/turbular/issues)
3. Submit pull requests with improvements
4. Help with documentation
5. Share your feedback

### Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed
- Use meaningful commit messages

### Roadmap
1. Add more testing, formatting and commit hooks
2. Add SSH support for database connection
3. Add APIs as datasources using [steampipe](https://steampipe.io/)
4. Enable local schema saving for databases to which the server has already connected
5. Add more datasources (snowflake, mongodb, excel, etc.)
6. Add authentication protection to routes

## 🧪 Testing

Run the test suite:
```bash
pytest
```

For development tests with the included PostgreSQL:
```bash
./scripts/test_connection.py
```

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Contributing Guide](CONTRIBUTING.md)

## 📝 Connection Examples

### PostgreSQL
```python
connection_info = {
    "database_type": "PostgreSQL",
    "username": "user",
    "password": "password",
    "host": "localhost",
    "port": 5432,
    "database_name": "mydb",
    "ssl": False
}
```

### BigQuery
```python
connection_info = {
    "database_type": "BigQuery",
    "path_cred": "/path/to/credentials.json",
    "project_id": "my-project",
    "dataset_id": "my_dataset"
}
```

### SQLite
```python
connection_info = {
    "type": "SQLite",
    "database_name": "my_database"
}
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- SQLAlchemy for database support
- [@henryclickclack](https://github.com/henryclickclack) [Henry Albert Jupiter Hommel](https://www.linkedin.com/in/henry-hommel-304675234/?originalSubdomain=de) as Co-Developer ❤️
- All our contributors and users

## 📞 Support

- Create an [issue](https://github.com/raeudigerRaeffi/turbular/issues)
- Email: raffael@turbular.com

---

<div align="center">
Made with ❤️ by the Turbular Team
</div>
