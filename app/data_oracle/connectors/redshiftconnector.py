import redshift_connector
from overrides import override

from .baseconnector import BaseDBConnector
from .connection_class import ConnectionInfo, RedshiftConnection, RedshiftConnectionSSO
from ..db_schema import Column, Table, Foreign_Key_Relation, parse_db_layout


class RedshiftConnector(BaseDBConnector):
    """
    Connector available for all redshift data warehouses
    """

    def __init__(self, redshift_connection_data: ConnectionInfo):
        super().__init__(redshift_connection_data)

    def connect(self, redshift_connection_data):
        if isinstance(redshift_connection_data, RedshiftConnection):
            return redshift_connector.connect(
                host=redshift_connection_data.host,
                database=redshift_connection_data.database,
                user=redshift_connection_data.user,
                password=redshift_connection_data.password
            )
        elif isinstance(redshift_connection_data, RedshiftConnectionSSO):
            pass
            # return redshift_connector.connect()
        else:
            raise Exception(f'Unknown connection data object of type {type(redshift_connection_data)}')

    @override
    def is_available(self) -> bool:
        """
        Returns Boolean whether connections is successful
        """
        return True

    @override
    def return_table_names(self, schema_name: str) -> list[str]:
        """
        Returns list of table names
        """
        table_query = self.execute_sql_statement(
            f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}';")
        return [table[0] for table in table_query[1:len(table_query)]]

    @override
    def return_schema_names(self) -> list[str]:
        blacklist = {'pg_catalog', 'information_schema'}
        schema_info_query = self.execute_sql_statement("SHOW SCHEMAS FROM DATABASE dev;")
        return [schemainfo[1] for schemainfo in schema_info_query[1:len(schema_info_query)] if
                schemainfo[1] not in blacklist]

    @override
    def return_view_names(self, schema_name: str) -> list[str]:
        return []

    @override
    def return_table_columns(self, schema_name: str, table_name, _table_type, scan_enums) -> Table:
        table_schema = self.execute_sql_statement(f"show table {schema_name}.{table_name};")[1][0].split("\n")[0:-1]

        table_schema[0] = f'CREATE TABLE {schema_name}.{table_name}('
        final_schema = [f"CREATE SCHEMA {schema_name};", "", f'CREATE TABLE {schema_name}.{table_name}(']
        for i in table_schema[1:-1]:

            user_col = "," in i
            col_info = i.split("ENCODE")[0].split("NOT NULL")[0].split("NULL")[0].rstrip().lstrip()
            if user_col and col_info[-1] != ",":
                col_info += ","

            final_schema.append(col_info)
        final_schema.append(")")
        cached_layout = "\n".join(final_schema)
        # print(cached_layout)
        if schema_name == "testpublic":
            print(table_schema)
            print(cached_layout)
        db_str_struct = parse_db_layout(cached_layout, default_schema=schema_name)
        table = table_name
        pk_name = db_str_struct[schema_name][table]["pk_name"]
        all_cached_cols = [db_str_struct[schema_name][table]["columns"][x] for x in
                           db_str_struct[schema_name][table]["columns"]]

        all_cached_cols = [Column(x["name"], x["type"], x["is_pk"], x["is_fk"], x["enums"]) for x in
                           all_cached_cols]

        cached_fk_relations = [Foreign_Key_Relation(**x) for x in db_str_struct[schema_name][table]["fk_relations"]]
        return Table(table, pk_name, all_cached_cols, _table_type, cached_fk_relations)

    @override
    def execute_sql_statement(self, _sql, _max_rows=None, autocommit=False):

        """
        @_sql:str
        Returns result of sql statement
        """
        returned_rows = []
        with self.connection.cursor() as cursor:
            cursor.execute(_sql)
            result: tuple = cursor.fetchall()
            returned_rows.append([x[0] for x in cursor.description])
            counter = 0
            for row in result:
                returned_rows.append(row)
                counter += 1
                if _max_rows is not None and _max_rows < counter:
                    break

            if autocommit:
                self.connection.commit()  # TODO check whether this applies to all previous sql executes

        return returned_rows
