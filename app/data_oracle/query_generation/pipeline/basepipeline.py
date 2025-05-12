from typing import NamedTuple, Dict

from .prompts import Intro_Prompt
from ...connectors import BaseDBConnector
from ...db_schema import Table, Database, translate_sql_args
from ...enums import Prompt_Type


class Example(NamedTuple):
    db: list[list[Table]]
    question: list[str]
    answer: list[str]


class PipelineSqlGen:

    def __init__(self, _connection: BaseDBConnector, scan_enums: bool = False, cached_schema: str | None = None):
        self.connection = _connection
        if cached_schema == None:
            self.db = _connection.scan_db(scan_enums)
        else:
            self.db = self.connection.return_cached_db(cached_schema)
        self.custom_prompt = None

    def reload_database(self) -> None:
        """
        Reloads database layout and copies over all relevant filters
        @return: None
        """
        filter_list = self.db.filter_list
        filter_active = self.db.filter_active
        ### TODO get all filters from table columns and apply them on reload

        new_db = self.connection.scan_db()
        new_db.filter_list = filter_list
        new_db.filter_active = filter_active
        for schema in new_db.schemas:
            schema.determine_filtered_elements(schema.tables)
            for table in schema.tables:
                table.determine_filtered_elements(table.columns)
        new_db.determine_filtered_elements(new_db.schemas)
        self.db = new_db

    def apply_schema_name_filter(self, schema_names: list[str]) -> list[str]:
        """
        Applies name filter to database
        @param schema_names: List of names to be filterd
        @return: List of tables that are now excluded via filter mechanism
        """
        self.db.apply_schema_name_filter(schema_names)
        return self.db.get_filtered_schemas()

    def apply_schema_regex_filter(self, _regex: str) -> list[str]:
        """
        Applies regex filter to name of tables in db
        @param _regex: regex string based on which the schema is filtered
        @return: List of tables that are now excluded via filter mechanism
        """
        self.db.apply_schema_regex_filter(_regex)
        return self.db.get_filtered_schemas()

    def apply_table_name_filter(self, filter_list: Dict[str, list[str]]) -> dict:
        """
        Applies name filter to database
        @param filter_list: List of names to be filterd
        @return: List of tables that are now excluded via filter mechanism
        """
        self.db.apply_table_name_filter(filter_list)
        return {schema.name: schema.get_filtered_tables() for schema in self.db.get_schemas()}

    def apply_table_regex_filter(self, _regex: Dict[str, str]) -> dict:
        """
        Applies regex filter to name of tables in db
        @param _regex: regex string based on which the table is filtered
        @return: List of tables that are now excluded via filter mechanism
        """
        self.db.apply_table_regex_filter(_regex)
        return {schema.name: schema.get_filtered_tables() for schema in self.db.get_schemas()}

    def apply_column_name_filter(self, filter_list: Dict[str, Dict[str, list[str]]]) -> dict:
        """
        Applies name filter to database
        @param filter_list: List of names to be filterd
        @return: List of tables that are now excluded via filter mechanism
        """
        self.db.apply_column_name_filter(filter_list)
        return {schema.name: {table.name: table.get_filtered_columns() for table in schema.get_tables()} for schema in
                self.db.get_schemas()}

    def apply_column_regex_filter(self, filter_regex: Dict[str, Dict[str, str]]) -> dict:
        """
        Applies regex filter to name of tables in db
        @param filter_regex: regex string based on which the table is filtered
        @return: List of tables that are now excluded via filter mechanism
        """
        self.db.apply_column_regex_filter(filter_regex)
        return {schema.name: {table.name: table.get_filtered_columns() for table in schema.get_tables()} for schema in
                self.db.get_schemas()}

    def set_custom_examples(self, examples: Example) -> None:
        """
        Based on a list of examples generate a custom few shot eample prompt
        @param examples: Example object containing all examples
        @return: None
        """
        custom_prompt = ""
        for i in range(len(examples["db"])):
            custom_prompt += f'Question: {examples["question"][i]} \n'

            new_db = Database("example")
            new_db.register_tables(examples["db"][i])
            custom_prompt += f'Database:\n{new_db.return_code_repr_schema()}\n'
            custom_prompt += f'Answer: {examples["answer"][i]}\n\n'
        self.custom_prompt = custom_prompt

    def overwrite_custom_examples(self, provided_examples: str)-> None:
        """
        Sets a new custom example prompt
        :param provided_examples: new prompt provided by the user
        :return: nothing
        """
        self.custom_prompt = provided_examples

    def return_db_prompt(self, normalized_names: bool = True) -> str:
        """
        Returns a database schema for a given database
        :param normalized_names: if true normalizes schema names to adhere to naming standards
        :return:
        """
        return self.db.return_code_repr_schema_normalized() if normalized_names else self.db.return_code_repr_schema()

    def normalize_query(self, sql_command: str) -> str:
        """
        Takes in a sql command for a normalized schema and translates it to the unnormalized schema
        :param sql_command: sql command as a string
        :return: sql query with unnormalized names
        """
        layout_translation_map = self.db.translations_map
        return translate_sql_args(sql_command, layout_translation_map, self.connection.type)

    def execute_sql_statement(self, sql_command: str, number_rows: int) -> list:
        """
        Executes a sql statement against the database and returns the results
        :param sql_command: sql command as a string
        :param number_rows: maximum number of rows to return
        :return: rows as a list of objects
        """
        return self.connection.execute_sql_statement(sql_command, number_rows)

    def generate_prompt(self, question: str, prompting_mode: Prompt_Type):
        prompt = ""
        prompt += Intro_Prompt
        if prompting_mode == Prompt_Type.CUSTOM:
            if self.custom_prompt is None:
                raise ValueError(f'If you want to use custom examples you need to set a custom prompt first with'
                                 f'set_examples()')
            prompt += self.custom_prompt
        elif prompting_mode == Prompt_Type.DYNAMIC:
            raise NotImplementedError("Not yet implemented")

        elif prompting_mode == Prompt_Type.FEW_SHOT:
            raise NotImplementedError("Not yet implemented")

        elif prompting_mode == Prompt_Type.ZERO_SHOT:
            pass

        prompt += f'Database:\n{self.return_db_prompt()}\n'
        prompt += f'Question: {question} \n'
        prompt += f'Answer: SELECT '

        return prompt
