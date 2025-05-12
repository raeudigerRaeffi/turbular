import re
from typing import Dict

from .base_db_class import BaseDbObject
from .filterobject import FilterObject, EmbeddingContainer
from .foreign_key_schema import Foreign_Key_Relation
from .utils import parse_db_layout, get_proper_naming
from ..enums import Filter_Type, Data_Table_Type


class FilterClass:

    def __init__(self):
        self.filter_active: bool = False
        self.filter_list: list[FilterObject] = []
        self.filtered_content: list[Schema | Table | Column] = []
        self.embedding_filter: EmbeddingContainer | None = None

    def release_filters(self) -> None:
        """
        Removes all active filters
        @return: None
        """
        self.filter_active = False
        self.filter_list = []
        self.filtered_content = []
        self.embedding_filter = None

    def determine_filtered_elements(self, content) -> None:
        """
        Determines which elements are not filtered
        @param content: list of tables or columns
        @return: None
        """
        filter_name_hashmap = {}
        regex_filters = []
        is_column = isinstance(content[0], Column)

        for _filter in self.filter_list:
            if _filter.classification == Filter_Type.NAME:
                for filter_name in _filter.value:
                    filter_name_hashmap[filter_name] = None
            elif _filter.classification == Filter_Type.REGEX:
                regex_filters.append(re.compile(_filter.value))

        for _item in content:
            matched_regex = False
            if is_column:
                if _item.is_pk or _item.is_fk:
                    self.filtered_content.append(_item)  # always include fk pk cols
                    continue
            for reg_patter in regex_filters:
                if reg_patter.match(_item.name):
                    matched_regex = True
            if _item.name not in filter_name_hashmap and not matched_regex:
                if self.embedding_filter is not None:
                    if self.embedding_filter.embedding @ _item.embedding.T <= self.embedding_filter.threshold:
                        self.filtered_content.append(_item)
                else:
                    self.filtered_content.append(_item)

    def apply_filter(self,
                     target,
                     content_names: list[str] = None,
                     regex_filter: str = None,
                     embedding_filter: FilterObject = None) -> None:
        """
        Function which applies an active function to the object
        @param embedding_filter: Fdy
        @param target: list of columns or tables
        @param content_names: list of object names
        @param regex_filter: regex pattern
        @return: None
        """
        self.filtered_content = []
        if content_names is None and regex_filter is None and embedding_filter is None:
            raise ValueError(f"The function needs to be called with a valid argument")
        if content_names is not None:
            new_filter = FilterObject(value=content_names, _type=Filter_Type.NAME)
            self.filter_list.append(new_filter)
        elif regex_filter is not None:
            new_filter = FilterObject(value=regex_filter, _type=Filter_Type.REGEX)
            self.filter_list.append(new_filter)
        else:
            self.embedding_filter = embedding_filter.value
        self.filter_active = True

        self.determine_filtered_elements(target)


class Column(BaseDbObject):
    def __init__(self, _name: str, _type, _is_pk=False, _is_fk: bool = False, _enums: list[str] = None):
        self.name = _name
        self.proper_name = get_proper_naming(_name)
        self.type = _type
        self.is_pk = _is_pk
        self.is_fk = _is_fk
        self.enums = _enums
        self.embedding = None

    def return_data(self) -> dict:
        """
        Returns dict representation of object
        @return: Dict containing all self variables
        """
        return vars(self)

    def return_sql_definition(self, use_normalized: bool) -> str:
        """
        Returns column sql def
        @return: str sql representation
        """
        if self.enums is not None:
            return f"""{self.proper_name if use_normalized else self.name} ENUM({",".join(['"' + str(x) + '"' for x in self.enums])})"""
        return f'{self.proper_name if use_normalized else self.name} {self.type}'

    @property
    def json_repr(self) -> {}:
        json_obj = {
            "name": self.name,
            "proper_name": self.proper_name,
            "data_type": self.type,
            "is_pk": self.is_pk,
            "is_fk": self.is_fk,
            "enum_values": self.enums
        }
        return json_obj


class Table(BaseDbObject, FilterClass):

    def __init__(self,
                 _name: str,
                 _pk_name: str | None,
                 _columns: list[Column],
                 _type: Data_Table_Type,
                 _fk_relations: list[Foreign_Key_Relation]
                 ):
        super().__init__()
        self.name = _name
        self.proper_name = get_proper_naming(_name)
        self.columns = _columns
        self.type = _type
        self.pk = [x for x in _columns if x.is_pk]  # pk can be composed of multiple columns
        self.pk_name = _pk_name
        self.fk_relations = _fk_relations
        self.embedding = None

    def get_cols(self) -> list[Column]:
        """
        Returns all columns based on active filters
        @return: All columns
        """
        if self.filter_active:
            return self.filtered_content
        return self.columns

    def return_columns_layout(self) -> list[dict]:
        return [x.return_data() for x in self.get_cols()]

    def has_pk(self) -> bool:
        """
        Returns whether the table has a primary key
        @return: Boolean indicating if primary key is present
        """
        return len(self.pk) > 0

    def apply_column_name_filter(self, _column_names: list[str]) -> None:
        """
        Applies filter which filters columns based on exact name matching
        @param _column_names: list of column names which are to be filtered
        @return: None
        """
        self.apply_filter(self.columns, content_names=_column_names)

    def apply_column_regex_filter(self, _regex_filter: str) -> None:
        """
        Applies filter which filters columns based on whether their name is matched by a regex pattern
        @param _regex_filter: string representation of regex pattern
        @return: None
        """
        self.apply_filter(self.columns, regex_filter=_regex_filter)

    def get_filtered_columns(self) -> list[str]:
        """
        Returns list of column names that are filtered out
        @return: list of column names
        """
        if self.filter_active:
            return [x.name for x in list(set(self.columns) - set(self.filtered_content))]
        else:
            return []

    def code_representation_str(self, schema_name: str | None, use_normalized: bool = False) -> str:
        _str_repr = ""
        if schema_name is None:
            table_name = self.proper_name if use_normalized else self.name
        else:
            table_name = f"{schema_name}.{self.proper_name}" if use_normalized else f"{schema_name}.{self.name}"
        _str_repr += f"CREATE TABLE {table_name}(\n"
        _str_repr += ",\n".join([x.return_sql_definition(use_normalized) for x in self.get_cols()])

        if self.has_pk():
            _str_repr += ",\n"
            if self.pk_name == None:
                _str_repr += f"PRIMARY KEY ({self.pk[0].proper_name if use_normalized else self.pk[0].name})"
            else:
                _str_repr += f"CONSTRAINT {self.pk_name} PRIMARY KEY ({','.join([x.proper_name if use_normalized else x.name for x in self.pk])})"
        if len(self.fk_relations) > 0:
            _str_repr += ",\n"
            _str_repr += ",\n".join([x.return_sql_definition(use_normalized) for x in self.fk_relations])
        _str_repr += "\n)"

        return _str_repr

    def apply_embedding_filter(self, embed_filter: FilterObject):
        self.apply_filter(self.columns, embedding_filter=embed_filter)

    @property
    def translations_map(self) -> {}:
        return {
            "name": self.name,
            "Columns": {
                x.proper_name: x.name for x in self.get_cols()
            }
        }

    @property
    def json_repr(self) -> {}:
        json_obj = {
            "name": self.name,
            "proper_name": self.proper_name,
            "pk_name": self.pk_name,
            "pk": {col.name for col in self.pk},
            "fk_relations": [fk_relation.json_repr for fk_relation in self.get_cols()],
            "columns": {column.name: column.json_repr for column in self.columns},

            # self.fk_relations = _fk_relations
        }
        return json_obj


class Schema(BaseDbObject, FilterClass):
    def __init__(self, _name: str, tables: list[Table]):
        super().__init__()
        self.name: str = _name
        self.proper_name = get_proper_naming(_name)
        self.tables: list[Table] = tables
        self.embedding = None
        self.cached_layout: str | None = None

    def apply_table_name_filter(self, _table_names: list[str]) -> None:
        """
        Applies a filter to remove all tables by exact name matching
        @param _table_names: list of table names
        @return: None
        """
        self.apply_filter(self.tables, content_names=_table_names)

    def apply_table_regex_filter(self, _regex_filter: str) -> None:
        """
        Applies a filter to remove all tables by regex pattern matching based on table name
        @param _regex_filter: regex string pattern
        @return: None
        """
        self.apply_filter(self.tables, regex_filter=_regex_filter)

    def apply_column_name_filter(self, filter_list: Dict[str, list[str]]) -> None:
        """
        Applies a exact name filter to columns in a given table. Table is specified in key and the applied filters in the value list
        @param filter_list: dict object with table name as key and list of column names as value
        @return: None
        """
        for table in self.tables:
            if table.name in filter_list:
                table.apply_column_name_filter(filter_list[table.name])

    def apply_column_regex_filter(self, filter_list: Dict[str, str]) -> None:
        """
        Applies a regex name filter to columns in a given table. Table is specified in key and the value is the regex pattern
        @param filter_list: dict object with table name as key and regex pattern as value
        @return:
        """
        for table in self.tables:
            if table.name in filter_list:
                table.apply_column_regex_filter(filter_list[table.name])

    def apply_embedding_filter(self,
                               nl_question: str,
                               embedding,
                               threshold: float,
                               applicable_table: bool) -> None:
        """

        @param nl_question:
        @param embedding:
        @param threshold:
        @param applicable_table:
        @return:
        """
        embed_filter = FilterObject(value=embedding,
                                    _type=Filter_Type.EMBEDDING,
                                    nl_question=nl_question,
                                    threshold=threshold
                                    )
        if applicable_table:
            self.apply_filter(self.tables, embedding_filter=embed_filter)
        for _table in self.tables:
            _table.apply_embedding_filter(embed_filter)

    def release_column_filters(self) -> None:
        """
        Releases all filters in the db
        @return:
        """
        for table in self.tables:
            table.release_filters()

    def get_filtered_tables(self) -> list[str]:
        """
        Determine which tables are removed by filters
        @return: list of table names
        """
        if self.filter_active:
            return [x.name for x in list(set(self.tables) - set(self.filtered_content))]
        else:
            return []

    def get_tables(self) -> list[Table]:
        """
        Get all tables based on active filters
        @return: list of Table objects
        """
        if self.filter_active:
            return self.filtered_content
        return self.tables

    def apply_embedding_model(self, embedding_callback) -> None:
        """
        Applies embedding model to all table names and column names and fills the respective embedding values
        @param embedding_callback callback which calculates embedding for a string input
        @return: None
        """
        for table in self.tables:
            table.embedding = embedding_callback(table.name)
            for column in table.columns:
                column.embedding = embedding_callback(column.name)

    def code_representation_str(self, use_normalized: bool) -> str:
        """
        Returns Sql representation of schema
        :param use_normalized: Boolean whether to enforce proper naming conventions
        :return: create schema string
        """
        return f"CREATE SCHEMA {self.proper_name if use_normalized else self.name};"

    def return_code_repr_schema(self, include_schema: bool, exclude_views=False) -> list[str]:
        """
        Displays a schemas as a list of  CREATE Table commands wrapped in a create
        schema call
        :param include_schema: Whether to include schema name in create table command
        :param exclude_views: Boolean to exclude Views from the list
        :return: list of  CREATE Table commands
        """

        _all_tables = self.get_tables()

        if exclude_views:
            view_filter = lambda x: True if x.type != Data_Table_Type.VIEW else False
            _all_tables = filter(view_filter, _all_tables)
        if include_schema:
            return [x.code_representation_str(self.name, False) for x in _all_tables]
        else:
            return [x.code_representation_str(None, False) for x in _all_tables]

    def return_code_repr_schema_normalized(self, include_schema: bool, exclude_views=False) -> list[str]:
        """
        Displays a database as a list of  CREATE Table commands
        :param include_schema: Whether to include schema name in create table command
        :param exclude_views: Boolean to exclude Views from the list
        :return: list of  CREATE Table commands
        """

        _all_tables = self.get_tables()
        if exclude_views:
            view_filter = lambda x: True if x.type != Data_Table_Type.VIEW else False
            _all_tables = filter(view_filter, _all_tables)
        if include_schema:
            return [x.code_representation_str(self.proper_name, True) for x in _all_tables]
        else:
            return [x.code_representation_str(None, True) for x in _all_tables]

    @property
    def translations_map(self) -> {}:
        translation_map = {"name": self.name,
                           "Tables": {}
                           }
        for table in self.tables:
            translation_map["Tables"][table.proper_name] = table.translations_map
        return translation_map

    @property
    def json_repr(self) -> {}:
        json_obj = {
            "name": self.name,
            "proper_name": self.proper_name,
            "tables": {table.name: table.json_repr for table in self.get_tables()},
        }
        return json_obj


class Database(BaseDbObject, FilterClass):
    def __init__(self, name: str):
        super().__init__()
        self.name: str = name
        self.proper_name = get_proper_naming(name)
        self.schemas: list[Schema] = []

    def register_schema(self, schema: Schema) -> None:
        """
        Appends schema to database obj
        @param schema: Table object
        @return: None
        """
        self.schemas.append(schema)

    def register_schemas(self, schemas: list[Schema]) -> None:
        """
        Appends list of schemas to registered schemas
        :param schemas: list of schema objects
        :return:
        """
        for schema in schemas:
            self.register_schema(schema)

    def apply_schema_name_filter(self, schema_names: list[str]) -> None:
        """
        Applies a filter to remove all schemas by exact name matching
        @param schema_names: list of table names
        @return: None
        """
        self.apply_filter(self.schemas, content_names=schema_names)

    def apply_schema_regex_filter(self, _regex_filter: str) -> None:
        """
        Applies a filter to remove all schemas by regex pattern matching based on table name
        @param _regex_filter: regex string pattern
        @return: None
        """
        self.apply_filter(self.schemas, regex_filter=_regex_filter)

    def apply_table_name_filter(self, filter_list: Dict[str, list[str]]) -> None:
        """
        Applies a filter to remove all tables by name
        :param filter_list: dict mapping schema to filtered table names
        :return: None
        """
        for schema in self.schemas:

            if schema.name in filter_list:
                schema.apply_table_name_filter(filter_list[schema.name])

    def apply_table_regex_filter(self, filter_list: Dict[str, str]) -> None:
        """
        Applies a filter to remove all tables by regex pattern matching based on table name
        @param filter_list: regex string pattern
        @return: None
        """
        for schema in self.schemas:
            if schema.name in filter_list:
                schema.apply_table_regex_filter(filter_list[schema.name])

    def apply_column_name_filter(self, filter_list: Dict[str, Dict[str, list[str]]]) -> None:
        """
        Applies a exact name filter to columns in a given table. Table is specified in key and the applied filters in
        the value list
        @param filter_list: dict object with schema name as key and table column dict as val
        @return: None
        """
        for schema in self.schemas:
            if schema.name in filter_list:
                schema.apply_column_name_filter(filter_list[schema.name])

    def apply_column_regex_filter(self, filter_list: Dict[str, Dict[str, str]]) -> None:
        """
        Applies a exact name filter to columns in a given table. Table is specified in key and the applied filters in the value list
        @param filter_list: dict object with schema name as key and table column dict as val
        @return: None
        """
        for schema in self.schemas:
            if schema.name in filter_list:
                schema.apply_column_regex_filter(filter_list[schema.name])

    def apply_embedding_filter(self,
                               nl_question: str,
                               embedding,
                               threshold: float,
                               applicable_table: bool) -> None:
        """

        @param nl_question:
        @param embedding:
        @param threshold:
        @param applicable_table:
        @return:
        """
        # todo fix this mess
        embed_filter = FilterObject(value=embedding,
                                    _type=Filter_Type.EMBEDDING,
                                    nl_question=nl_question,
                                    threshold=threshold
                                    )
        if applicable_table:
            self.apply_filter(self.schemas, embedding_filter=embed_filter)
        for schema in self.schemas:
            schema.apply_embedding_filter(embed_filter)  ##

    def release_table_filters(self) -> None:
        """
        Releases all filters in the db
        @return:
        """
        for schema in self.schemas:
            schema.release_filters()

    def release_filters(self) -> None:
        """
        Releases all filters in the db
        @return:
        """
        super().release_filters()
        for schema in self.schemas:
            schema.release_filters()
            for table in schema.tables:
                table.release_filters()

    def get_filtered_schemas(self) -> list[str]:
        """
        Determine which tables are removed by filters
        @return: list of table names
        """
        if self.filter_active:
            return [x.name for x in list(set(self.schemas) - set(self.filtered_content))]
        else:
            return []

    def get_schemas(self) -> list[Schema]:
        """
        Get all tables based on active filters
        @return: list of Table objects
        """
        if self.filter_active:
            return self.filtered_content
        return self.schemas

    def apply_embedding_model(self, embedding_callback) -> None:
        """
        Applies embedding model to all schema. column, table names and fills the respective embedding values
        @param embedding_callback callback which calculates embedding for a string input
        @return: None
        """
        for schema in self.schemas:
            schema.embedding = embedding_callback(schema.name)
            for table in schema.tables:
                table.embedding = embedding_callback(table.name)
                for column in table.columns:
                    column.embedding = embedding_callback(column.name)

    ## Need to change approach first list of create schema statements
    # then list of create table statements. each table name is represented as
    # schema.tablenames
    def return_code_repr_schema(self, exclude_views=False) -> str:
        """
        Represents a database as a set of Create Schema calls.
        :param exclude_views:
        :return:
        """
        all_schemas = self.get_schemas()

        create_schemas = "\n".join(schema.code_representation_str(False) for schema in all_schemas)

        return create_schemas + "\n\n" + "\n\n".join(
            [table_schema for schema in all_schemas for table_schema in
             schema.return_code_repr_schema(include_schema=True)])

    def return_code_repr_schema_normalized(self, exclude_views=False) -> str:
        """
        Represents a database as a set of Create Schema calls.
        :param exclude_views:
        :return:
        """
        all_schemas = self.get_schemas()
        create_schemas = "\n".join(schema.code_representation_str(True) for schema in all_schemas)
        return create_schemas + "\n\n" + "\n\n".join(
            [table_schema for schema in all_schemas for table_schema in
             schema.return_code_repr_schema_normalized(include_schema=True)])

    def reload_from_cache(self, cached_layout: str):
        self.schemas = []
        db_str_struct = parse_db_layout(cached_layout)
        for schema_name in db_str_struct:
            tables_in_schema = []
            for table in db_str_struct[schema_name]:
                pk_name = db_str_struct[schema_name][table]["pk_name"]
                all_cached_cols = [db_str_struct[schema_name][table]["columns"][x] for x in
                                   db_str_struct[schema_name][table]["columns"]]

                all_cached_cols = [Column(x["name"], x["type"], x["is_pk"], x["is_fk"], x["enums"]) for x in
                                   all_cached_cols]

                cached_fk_relations = [Foreign_Key_Relation(**x) for x in
                                       db_str_struct[schema_name][table]["fk_relations"]]
                cached_table = Table(table, pk_name, all_cached_cols, Data_Table_Type.TABLE, cached_fk_relations)
                tables_in_schema.append(cached_table)
            self.register_schema(Schema(schema_name, tables_in_schema))

    @property
    def translations_map(self) -> {}:
        translation_map = {}
        for schema in self.schemas:
            translation_map[schema.proper_name] = schema.translations_map
        return translation_map

    @property
    def json_repr(self) -> {}:
        json_obj = {
            "name": self.name,
            "proper_name": self.proper_name,
            "schemas": {schema.name: schema.json_repr for schema in self.get_schemas()},
        }
        return json_obj
