from fastapi import HTTPException

from app.data_oracle import RedshiftConnector, RedshiftConnection, ConnectionDetails, \
    SqlAlchemyConnector, BigQueryConnection
from app.data_oracle.query_generation import PipelineSqlGen
from app.fastapitypes.sql_connection import Db_Connection_Args


def get_sqlalchemy_connection(sql_args: ConnectionDetails) -> SqlAlchemyConnector:
    """
    Returns a SqlAlchemyConnector object.
    @sql_args: holds all necessary args for connection
    Return: connection object for sqlalchemy db
    """
    if sql_args.ssl:
        sql_args.ssl_credentials = '/etc/ssl/certs/ca-certificates.crt'
    return SqlAlchemyConnector(sql_args)


def get_redshift_connection(redshift_args: RedshiftConnection) -> RedshiftConnector:
    """
    Returns a RedshiftConnector object.
    @redshift_args: holds all necessary args for connection
    Return: connection object for redshift db
    """
    return RedshiftConnector(redshift_args)


async def get_db_pipeline(db_con_args: Db_Connection_Args, cached_schema: str | None = None) -> PipelineSqlGen:
    if isinstance(db_con_args, ConnectionDetails):
        db_connection = get_sqlalchemy_connection(db_con_args)
    elif isinstance(db_con_args, BigQueryConnection):
        raise HTTPException(status_code=400, detail="Not implemented yet")
    elif isinstance(db_con_args, RedshiftConnection):
        db_connection = get_redshift_connection(db_con_args)
    else:
        # This should theoretically never happen if types are correctly defined
        raise HTTPException(status_code=400, detail="Unexpected connection type")

    return PipelineSqlGen(db_connection, False, cached_schema)
