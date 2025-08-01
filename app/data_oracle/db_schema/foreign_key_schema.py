from .base_db_class import BaseDbObject
from .utils import get_proper_naming


class Foreign_Key_Relation(BaseDbObject):
    def __init__(self, _cols: list[str] | set, ref_table: str, ref_schema: str, ref_cols: list[str]):
        self.constrained_columns = _cols
        self.referred_table = ref_table
        self.referred_schema = ref_schema
        self.referred_columns = ref_cols

    def return_sql_definition(self, use_normalized: bool) -> str:
        if use_normalized:
            referred_table_name = f"{self.referred_schema}.{get_proper_naming(self.referred_table)}"
        else:
            referred_table_name = f"{self.referred_schema}.{self.referred_table}"
        _out = f'FOREIGN KEY ({",".join([get_proper_naming(x) if use_normalized else x for x in self.constrained_columns])}) REFERENCES '
        _out += f'{referred_table_name}({",".join([get_proper_naming(x) if use_normalized else x for x in self.referred_columns])})'
        return _out

    @property
    def json_repr(self):
        json_obj = {
            "constrained_columns_name": self.constrained_columns,
            "constrained_columns_proper_name": [get_proper_naming(col) for col in self.constrained_columns],
            "referred_table_name": self.referred_table,
            "referred_schema_name": self.referred_schema,
            "referred_table_proper_name": get_proper_naming(self.referred_table)
        }
        return json_obj
