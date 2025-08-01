from pydantic import BaseModel
from enum import Enum

from app.data_oracle import ConnectionDetails, BigQueryConnection, RedshiftConnection, FileConnection

Db_Connection_Args = ConnectionDetails |  BigQueryConnection | RedshiftConnection | FileConnection


class SupportedDb(str, Enum):
    mysql = "MySQL"
    postgresql = "PostgreSQL"
    oracle = "Oracle"
    mssql = "MsSql"
    sqlite = "SQLite"
    bigquery = "BigQuery"
    redshift = "Redshift"

class SupportedSSHKey(str, Enum):
    rsa = "RSA"
    ed25519 = "Ed25519"
    ecdsa = "ECDSA"
    dss = "DSS"
