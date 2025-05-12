from pydantic import BaseModel
from typing import Optional, Dict
from sqlalchemy import URL

class ConnectionDetails(BaseModel):
    database_type: str
    username: str
    password: str
    host: str
    port: int
    database_name: str
    ssl: bool = False
    ssl_credentials: Optional[str] = None

    def create_url(self, driver: str, suffix: Dict = {}):
        return URL.create(
            driver,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database_name,
            query=suffix,
        )

class FileConnection(BaseModel):
    path: str
    database_name: str
    type: str = "SQLite"

class BigQueryConnection(BaseModel):
    database_type: str = "BigQuery"
    path_cred: str
    project_id: str
    dataset_id: str

    @property
    def database_name(self):
        return self.project_id

class RedshiftConnection(BaseModel):
    host: str
    database: str
    user: str
    password: str

    @property
    def database_name(self):
        return self.database

class RedshiftConnectionSSO(BaseModel):
    host: str
    database: str

    @property
    def database_name(self):
        return self.database

ConnectionInfo = ConnectionDetails | FileConnection | BigQueryConnection | RedshiftConnection | RedshiftConnectionSSO
