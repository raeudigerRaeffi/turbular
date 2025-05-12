import datetime
import decimal

from overrides import override
from sqlalchemy import create_engine, inspect, text

from .baseconnector import BaseDBConnector
from .connection_class import ConnectionInfo, ConnectionDetails, FileConnection
from ..db_schema import Column, Table, Foreign_Key_Relation
from ..enums import Data_Table_Type


class SqlAlchemyConnector(BaseDBConnector):
    """
    Connector available for all Sql Dbs that can be accessed with Sqlalchemy
    """

    def __init__(self, connection_data: ConnectionInfo):
        super().__init__(connection_data)
        self.inspection = inspect(self.connection)
        self.fk_relations = {}
        self.pk = {}

    @override
    def connect(self, connection_data):
        drivername_mapper = {
            'MySQL': 'mysql+pymysql',
            'PostgreSQL': 'postgresql+psycopg',
            'Oracle': 'oracle+oracledb',
            'MsSql': 'mssql+pyodbc',
            'SQLite': 'sqlite'
        }
        # Snowflake https://stackoverflow.com/questions/70228997/how-to-connect-sqlalchemy-to-snowflake-database-using-oauth2
        if type(connection_data) == ConnectionDetails:
            suffix = {}
            if connection_data.database_type == "MsSql":
                suffix = {"driver": "ODBC Driver 17 for SQL Server", "TrustServerCertificate": "yes"}
            driver = drivername_mapper[connection_data.database_type]
            self.type = connection_data.database_type
            url_object = connection_data.return_url_string(driver, suffix=suffix)

            if connection_data.ssl:
                if connection_data.database_type == 'MySQL':
                    ssl_args = {"ssl": {
                        # or change to verify-ca or verify-full based on your requirement
                        'ca': connection_data.ssl_credentials,  # path to your .crt file
                    }}
                elif connection_data.database_type == 'PostgreSQL':
                    ssl_args = {
                        'sslmode': 'prefer',
                        'sslrootcert': connection_data.ssl_credentials
                    }
                else:
                    ssl_args = {}
                return create_engine(url_object, connect_args=ssl_args)

            return create_engine(url_object)
        elif type(connection_data) == FileConnection:
            return create_engine("sqlite:///" + connection_data.path)

    @override
    def is_available(self):
        """
        Returns Boolean whether connections is successful
        """
        try:
            with self.connection.connect() as conn:
                pass

            return True
        except:
            return False

    @override
    def return_table_names(self, schema_name: str) -> list[str]:
        """
        Returns list of table names and detects fk and pk columns
        """
        table_names = self.inspection.get_table_names(schema_name)
        for _table in table_names:
            self.pk[_table] = {x: x for x in
                               self.inspection.get_pk_constraint(_table, schema_name)["constrained_columns"]}
            self.fk_relations[_table] = {}
            fk_relations = self.inspection.get_foreign_keys(_table, schema_name)
            for fk_relation in fk_relations:
                for _col in fk_relation["constrained_columns"]:
                    self.fk_relations[_table][_col] = fk_relation["referred_table"]

        return table_names

    @override
    def return_view_names(self, schema_name: str) -> list[str]:
        """
        Returns list of view names
        """
        view_names = self.inspection.get_view_names(schema_name)
        for _table in view_names:
            self.pk[_table] = {x: x for x in
                               self.inspection.get_pk_constraint(_table, schema_name)["constrained_columns"]}
            self.fk_relations[_table] = {}
            fk_relations = self.inspection.get_foreign_keys(_table, schema_name)
            for fk_relation in fk_relations:
                for _col in fk_relation["constrained_columns"]:
                    self.fk_relations[_table][_col] = fk_relation["referred_table"]

        return view_names

    @override
    def return_schema_names(self) -> list[str]:
        blacklist = {'information_schema', 'INFORMATION_SCHEMA'}
        if self.connection_data.database_type == "MsSql":
            blacklist = blacklist | {'db_accessadmin', 'db_backupoperator', 'db_datareader', 'db_datawriter',
                                     'db_ddladmin', 'db_denydatareader',
                                     'db_denydatawriter', 'db_owner', 'db_securityadmin', 'guest', 'sys'}
        return [schemaname for schemaname in self.inspection.get_schema_names() if schemaname not in blacklist]

    def scan_columns_enum(self, schema_name: str, col_list: list[Column], table_name: str):
        max_row_select = 700
        max_col_scan_size = 300

        def column(matrix, i, max_row):
            return [row[i] for row_i, row in enumerate(matrix, 1) if row_i < max_row]

        statement = f"SELECT * FROM {schema_name}.{table_name} LIMIT {max_row_select}"
        with self.connection.connect() as conn:
            sql_res_conn = conn.execute(text(statement))
            valid_data_types = ["string", "text"]
            sql_res = list(sql_res_conn)
            for _index, _col in enumerate(col_list):
                if any(x in _col.type.lower() for x in valid_data_types):
                    counting_set = set()
                    col_data = column(sql_res, _index, max_col_scan_size)
                    for data_point in col_data:
                        counting_set.add(data_point)
                    comparison_size = max_col_scan_size if max_col_scan_size > len(sql_res) else len(sql_res)
                    if len(counting_set) <= 0.1 * comparison_size:
                        empty_field = 0
                        counting_set = set()
                        # go over all data now
                        col_data = column(sql_res, _index, max_row_select)
                        for data_point in col_data:
                            counting_set.add(data_point)
                            if data_point == "":
                                empty_field += 1
                        if (len(counting_set) + empty_field) <= 0.1 * comparison_size:
                            _col.enums = list(counting_set)

        return col_list

    def return_all_table_column_info(self, schema_name: str, table_name: str) -> list[Column]:
        out = []
        all_cols = self.inspection.get_columns(table_name, schema_name)
        for _col in all_cols:
            col_type = str(_col["type"])
            _name = _col["name"]
            _is_pk = False
            _is_fk = False
            _fk_to = None
            if _name in self.fk_relations[table_name]:
                _is_fk = True
            if _name in self.pk[table_name]:
                _is_pk = True

            new_col = Column(_name, str(col_type), _is_pk, _is_fk)
            out.append(new_col)

        return out

    @override
    def return_table_columns(self, schema_name: str, table_name: str, _table_type: Data_Table_Type,
                             scan_enums: bool) -> Table:
        """
        Returns list of columns of table
        """
        all_info = self.return_all_table_column_info(schema_name, table_name)

        if scan_enums:
            all_info = self.scan_columns_enum(schema_name, all_info, table_name)

        _pk_name = self.inspection.get_pk_constraint(table_name, schema_name)['name']
        fk_relations = [Foreign_Key_Relation(
            x["constrained_columns"],
            x["referred_table"],
            x["referred_schema"],
            x["referred_columns"])
            for x in self.inspection.get_foreign_keys(table_name, schema_name)]
        return Table(table_name, _pk_name, all_info, _table_type, fk_relations)

    def convert_value(self, _input):
        """
        Function to convert object types of sqlalchemy to primitive types
        :param _input:
        :return: _input
        """
        if isinstance(_input, decimal.Decimal):
            return float(_input)
        elif isinstance(_input, datetime.datetime):
            try:
                return _input.strftime("%d/%m/%Y %H:%M")
            except Exception as e:
                return str(_input)
        elif isinstance(_input, datetime.date):
            return str(_input)
        else:
            return _input

    @override
    def execute_sql_statement(self, _sql, _max_rows=None):

        """
        @_sql:str
        Returns result of sql statement
        """
        results = []

        with self.connection.connect() as conn:
            sql_res_conn = conn.execute(text(_sql))
            results.append([x for x in sql_res_conn.keys()])
            counter = 0
            for _row in sql_res_conn:

                _row = [self.convert_value(x) for x in _row]
                # do i need to account for datetime.datetime,datetime.date,datetime.time, datetime.timedelta too ?
                results.append(_row)
                counter += 1
                if _max_rows is not None and _max_rows < counter:
                    break

        return results

#    def __del__(self):
#       self.connection.dispose()
