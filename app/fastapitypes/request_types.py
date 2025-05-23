
from pydantic import BaseModel
from typing import Optional
from app.fastapitypes.sql_connection import Db_Connection_Args


class ExecuteQueryRequest(BaseModel):
    db_info: Db_Connection_Args
    query: str
    normalized_query: bool
    max_rows: int
    autocommit: bool = False
    unormalized_schema: Optional[str] = None