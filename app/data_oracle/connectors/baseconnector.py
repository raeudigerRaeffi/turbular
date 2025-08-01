from abc import ABC

from .connection_class import ConnectionInfo
from ..db_schema import Database, Table, Schema
from ..enums import Data_Table_Type


class BaseDBConnector(ABC):

    def __init__(self, connection_data: ConnectionInfo):
        self.connection_data = connection_data
        self.type = None
        self.connection = self.connect(connection_data)
        self.db = self.register_db(connection_data)
        self.ssh_connection = None

    def connect(self, connection_data: ConnectionInfo):
        """
        Returns a connection object to DB
        """
        pass

    def register_db(self, connection_data: ConnectionInfo):
        return Database(connection_data.database_name)

    def is_available(self):
        """
        Returns Boolean whether connections is successful
        """
        pass

    def return_table_names(self, schema_name: str) -> list[str]:
        """
        Returns list of table names
        """
        pass

    def return_view_names(self, schema_name: str) -> list[str]:
        """
        Returns list of view names
        """
        pass

    def return_table_columns(self, schema_name: str, table_name: str, _table_type: Data_Table_Type,
                             scan_enums: bool) -> Table:
        """
        @table_name:str
        Returns list of columns of table
        """
        pass

    def execute_sql_statement(self, _sql, _max_rows, autocommit=False):
        """
        @_sql:str
        Returns result of sql statement
        """
        pass

    def return_table_column_info(self, schema_name: str, scan_enums: bool) -> list[Table]:
        """
        Returns dictionary containing table_name : [column_name] pairs
        """
        all_tables = self.return_table_names(schema_name)
        return [self.return_table_columns(schema_name, table, Data_Table_Type.TABLE, scan_enums) for table in
                all_tables]

    def return_view_column_info(self, schema_name: str, scan_enums: bool) -> list[Table]:
        """
        Returns list containing table_name : [column_name] pairs
        """
        all_tables = self.return_view_names(schema_name)
        return [self.return_table_columns(schema_name, table, Data_Table_Type.VIEW, scan_enums) for table in all_tables]

    def return_db_layout(self) -> Database:
        return self.db

    """
    def scan_db(self, scan_enums=False) -> Database:
        self.db.register_tables(self.return_view_column_info(scan_enums))
        self.db.register_tables(self.return_table_column_info(scan_enums))
        return self.return_db_layout()
    """

    def return_schema_names(self) -> list[str]:
        pass

    def return_schemas(self, scan_enums: bool) -> list[Schema]:
        output_schemas = []
        all_schemas = self.return_schema_names()
        for schema in all_schemas:
            all_tables = self.return_table_column_info(schema, scan_enums) + self.return_view_column_info(schema,
                                                                                                          scan_enums)
            if len(all_tables) > 0:
                output_schemas.append(Schema(schema, all_tables))  # we skip empty schemas
        return output_schemas

    def scan_db(self, scan_enums: bool = False) -> Database:
        """
        Populates db object with information about the schema and returns it
        :param scan_enums: Param to manually scan entries to find potential enum values
        :return:
        """
        self.db.register_schemas(self.return_schemas(scan_enums))
        return self.return_db_layout()

    def return_cached_db(self, cached_layout: str) -> Database:
        self.db = self.register_db(self.connection_data)
        self.db.reload_from_cache(cached_layout)
        return self.return_db_layout()
