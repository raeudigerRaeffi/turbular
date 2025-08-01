import datetime
import decimal

from google.cloud import bigquery
from google.oauth2 import service_account
from overrides import override

from .baseconnector import BaseDBConnector
from .connection_class import ConnectionInfo, BigQueryConnection
from ..db_schema import Column, Table, Foreign_Key_Relation
from ..enums import Data_Table_Type


class BigQueryConnector(BaseDBConnector):
    def __init__(self, big_query_connection_data: ConnectionInfo):
        super().__init__(big_query_connection_data)
        self.db_id = f"{big_query_connection_data.project_id}"  # .{big_query_connection_data.database_id}"
        self.detect_column_constraints()

    def detect_column_constraints(self):
        self.pk_constraints = {}
        self.fk_constraints = {}

        query_col_constraint = f"SELECT * FROM {self.connection_data.database_id}.INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE;"
        query_col_usage = f"SELECT * FROM {self.connection_data.database_id}.INFORMATION_SCHEMA.KEY_COLUMN_USAGE;"

        for usage_row in self.connection.query_and_wait(query_col_usage):

            _type_constraint, type_id = usage_row.constraint_name.split(".")[1].split("$")

            if _type_constraint == "pk":
                if usage_row.table_name in self.pk_constraints:
                    self.pk_constraints[usage_row.table_name].add(usage_row.column_name)
                else:
                    self.pk_constraints[usage_row.table_name] = {usage_row.column_name}
            elif _type_constraint == "fk":
                if usage_row.constraint_name in self.fk_constraints:
                    self.fk_constraints[usage_row.constraint_name]["fk"].constrained_columns.add(
                        usage_row.column_name)

                else:
                    self.fk_constraints[usage_row.constraint_name] = {
                        "fk": Foreign_Key_Relation(**{"_cols": {usage_row.column_name},
                                                      "ref_table": "",
                                                      "ref_schema": "",
                                                      "ref_cols": []
                                                      }),
                        "origin": usage_row.table_name}

        for constraint_row in self.connection.query_and_wait(query_col_constraint):

            _type_constraint, type_id = constraint_row.constraint_name.split(".")[1].split("$")
            if _type_constraint == "fk":
                self.fk_constraints[constraint_row.constraint_name]["fk"].referred_columns.append(
                    constraint_row.column_name)
                self.fk_constraints[constraint_row.constraint_name]["fk"].referred_table = constraint_row.table_name
                self.fk_constraints[constraint_row.constraint_name]["fk"].referred_schema = constraint_row.table_schema
        int_dict = {}
        for _key in self.fk_constraints:
            table_key = self.fk_constraints[_key]["origin"]
            if table_key in int_dict:
                int_dict[table_key].append(self.fk_constraints[_key]["fk"])
            else:
                int_dict[table_key] = [self.fk_constraints[_key]["fk"]]
        self.fk_constraints = int_dict

    def connect(self, big_query_connection_data: BigQueryConnection):
        credentials = service_account.Credentials.from_service_account_file(
            big_query_connection_data.path_cred
        )

        return bigquery.Client(credentials=credentials, project=big_query_connection_data.project_id)

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
        return [x.table_id for x in self.connection.list_tables(f"{self.db_id}.{schema_name}") if
                x.table_type == "TABLE"]

    @override
    def return_view_names(self, schema_name: str) -> list[str]:
        """
        Returns list of view names
        """
        return [x.table_id for x in self.connection.list_tables(f"{self.db_id}.{schema_name}") if
                x.table_type == "VIEW"]

    @override
    def return_table_columns(self, schema_name: str, table_name: str, _table_type: Data_Table_Type,
                             scan_enums: bool) -> Table:
        all_info = []
        fk_relations = []
        for _col in self.connection.get_table(f"{self.db_id}.{schema_name}.{table_name}").schema:
            col_type = str(_col.field_type)
            _name = _col.name
            _is_pk = False
            _is_fk = False
            _fk_to = None
            if table_name in self.pk_constraints:
                if _name in self.pk_constraints[table_name]:
                    _is_pk = True
            if table_name in self.fk_constraints:
                for _fk_constraint in self.fk_constraints[table_name]:
                    if _name in self.fk_constraints[table_name][_fk_constraint].constrained_columns:
                        _is_fk = True
            all_info.append(Column(_name, str(col_type), _is_pk, _is_fk))

        if table_name in self.fk_constraints:
            fk_relations = self.fk_constraints[table_name]

        return Table(f"{table_name}", None, all_info, _table_type, fk_relations)

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
            try:
                return _input.strftime("%d/%m/%Y")
            except Exception as e:
                return str(_input)
        else:
            return _input

    @override
    def return_schema_names(self) -> list[str]:
        return [x.dataset_id for x in self.connection.list_datasets()]

    @override
    def execute_sql_statement(self, _sql, _max_rows=None, autocommit=True):
        """
        @_sql:str
        Returns result of sql statement
        """
        if not autocommit:
            raise Warning(f"BigQuery always autocommits, the behavious can not be disabled")
        results = []
        counter = 0
        for usage_row in self.connection.query_and_wait(_sql):
            if counter == 0:
                results.append([x for x in usage_row.keys()])
            counter += 1
            results.append([self.convert_value(x) for x in list(usage_row.values())])
            if counter > _max_rows:
                break
        return results
