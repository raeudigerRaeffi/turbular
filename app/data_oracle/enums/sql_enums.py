from .base_enum import BaseEnum





class Sql_Alchemy_Types(BaseEnum):
    MYSQL = 'MySQL'
    POSTGRESQL = 'PostgreSQL'
    ORACLE = 'Oracle'
    MICROSOFTSQLSERVER = 'Microsoft SQL Server'
    SQLITE = 'SQLite'

class Sql_Types(BaseEnum):
    MYSQL = 'MySQL'
    POSTGRESQL = 'PostgreSQL'
    ORACLE = 'Oracle'
    MICROSOFTSQLSERVER = 'Microsoft SQL Server'
    SQLITE = 'SQLite'
    BIGQUERY = 'BigQuery'
    REDSHIFT = 'Redshift'

class data_types(BaseEnum):
    INTEGER = "INT"
    VARCHAR = "VARCHAR"
    DATE = "DATE"

class Data_Table_Type(BaseEnum):
    TABLE = "Table"
    VIEW = "View"


