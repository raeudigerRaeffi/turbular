from enum import Enum
from pydantic import BaseModel


class DataSource(str, Enum):
    excel = "Excel"
    db = "DB"
    api = "Api"

class SupportedDb(str, Enum):
    mysql = "MySQL"
    postgresql = "PostgreSQL"
    oracle = "Oracle"
    mssql = "MsSql"
    sqlite = "SQLite"
    bigquery = "BigQuery"
    redshift = "Redshift"

class DatabaseArgs(BaseModel):
    """
    Typing class specifying the arguments to be provided to make a connection to a database
    """
    db_type: SupportedDb
    db_name: str
    db_user: str
    password: str
    host: str
    port: int
    use_ssl: bool
