from app.data_oracle.db_schema import Column, Table


def test_apply_filter():
    column_list = [
        Column("Col1", "INTEGER", True, True),
        Column("Col2", "INTEGER"),
        Column("Col3", "INTEGER"),
        Column("Col4", "INTEGER"),
        Column("Test1", "INTEGER"),
        Column("Test2", "INTEGER", True, True),
    ]
    table = Table("T1", None, column_list, "Table", [])
    table.apply_column_name_filter(["Col1", "Col2"])
    table.apply_column_regex_filter("Test[0-9]+")
    assert set(["Col1", "Col3", "Col4", "Test2"]) == set([x.name for x in table.get_cols()])


def test_release_filter():
    column_list = [
        Column("Col1", "INTEGER", True, True),
        Column("Col2", "INTEGER"),
        Column("Col3", "INTEGER"),
        Column("Col4", "INTEGER"),
        Column("Test1", "INTEGER"),
        Column("Test2", "INTEGER", True, True),
    ]
    table = Table("T1", None, column_list, "Table", [])
    table.apply_column_name_filter(["Col1", "Col2"])
    table.apply_column_regex_filter("Test[0-9]+")
    table.release_filters()
    assert set([]) == set([x.name for x in table.filtered_content])
