from app.data_oracle.db_schema import Column, Table, Database, Schema
from app.data_oracle.query_generation import PipelineSqlGen


class MockConnection():
    def __init__(self):
        pass

    def scan_db(self, boolean: bool):
        return None


def test_init():
    mock_conn = MockConnection()
    pipeline = PipelineSqlGen(mock_conn)
    assert True == True


def test_pipeline_table_apply_filter():
    mock_conn = MockConnection()
    pipeline = PipelineSqlGen(mock_conn)
    column_list = [
        Column("Col1", "INTEGER"),
        Column("Col2", "INTEGER"),
        Column("Col3", "INTEGER"),
        Column("Col4", "INTEGER")
    ]
    table_list = [
        Table("T1", None, column_list, "Table", []),
        Table("T2", None, column_list, "Table", []),
        Table("T3", None, column_list, "View", []),
        Table("Test2", None, column_list, "View", []),
    ]
    schema_list = [Schema("pub", table_list), Schema("pubmore", table_list)]
    scanned_db = Database("test")  #
    scanned_db.register_schemas(schema_list)

    pipeline.db = scanned_db
    pipeline.apply_table_name_filter({"pub": ["Persons", "T1"]})
    pipeline.apply_table_name_filter({"pub": ["Test3", "Test4"], "pubmore": ["Test3", "Test4"]})
    pipeline.apply_table_regex_filter({"pub": "Test[0-9]+", "pubmore": "Test[0-9]+"})
    assert ["pub", "pubmore"] == [x.name for x in pipeline.db.get_schemas()]
    assert {"pub": set(["Test2", "T1"]), "pubmore": set(["Test2"])} == {schema.name: set(schema.get_filtered_tables())
                                                                        for schema in
                                                                        pipeline.db.get_schemas()}


def test_pipeline_table_apply_filter():
    mock_conn = MockConnection()
    pipeline = PipelineSqlGen(mock_conn)
    column_list = [
        Column("Col1", "INTEGER"),
        Column("Col2", "INTEGER"),
        Column("Col3", "INTEGER"),
        Column("Col4", "INTEGER")
    ]
    table_list = [
        Table("T1", None, column_list, "Table", []),
        Table("T2", None, column_list, "Table", []),
        Table("T3", None, column_list, "View", []),
        Table("Test2", None, column_list, "View", []),
    ]
    schema_list = [Schema("pub", table_list), Schema("pubmore", table_list)]
    scanned_db = Database("test")  #
    scanned_db.register_schemas(schema_list)

    pipeline.db = scanned_db

    pipeline.apply_schema_name_filter(["pub"])
    assert {"pubmore": {"Test2", "T1", "T2", "T3"}} == {schema.name: {x.name for x in schema.get_tables()}
                                                        for schema in
                                                        pipeline.db.get_schemas()}
