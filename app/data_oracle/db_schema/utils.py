import re

from sqlglot import parse_one, exp
from sqlglot.optimizer import optimize


def parse_db_layout(db_layout: str, default_schema: str | None = None) -> {}:
    # Split the layout into table creation commands

    dbinfo = {}  # Dictionary to accumulate parsed table information
    table_commands = re.split(r'CREATE TABLE', db_layout)

    schema_commands = re.split(r'CREATE SCHEMA', table_commands.pop(0))  # first elememts contains all schemas
    for schem in schema_commands[1:len(schema_commands)]:  # first element is empty
        dbinfo[re.search(r'(\w+)\s*\;', schem).group(1)] = {}

    for command in table_commands:
        lines = command.splitlines()[1:-1]  # Trim the leading and trailing lines
        schema_name, table_name = re.search(r'(\b\w+\.\w+)\(', command).group(1).split(".")
        columns = {}
        fk_relations = []
        pk_name = None
        for line in lines:
            if line.startswith('PRIMARY KEY'):
                primary_keys = line.replace("PRIMARY KEY (", "").replace(")", "")
                if primary_keys[-1] == ",":
                    primary_keys = primary_keys[0:len(primary_keys) - 1]
                primary_keys = primary_keys.split(",")
                for extracted_pk in primary_keys:  # one item loop not necessary
                    columns[extracted_pk]["is_pk"] = True

            elif line.startswith('FOREIGN KEY'):
                fk_relation_obj = {"_cols": [], "ref_table": "", "ref_cols": []}
                local_columns, foreign_cols = line.split(" REFERENCES ")
                if foreign_cols[-1] == ",":
                    foreign_cols = foreign_cols[0:len(foreign_cols) - 1]
                local_columns = local_columns.replace("FOREIGN KEY (", "").replace(")", "").split(",")

                foreign_cols = foreign_cols.split("(")

                if default_schema != None:
                    splitted_referred_table = foreign_cols[0].split(".")
                    if len(splitted_referred_table) > 1:
                        referred_schema, referred_table = splitted_referred_table
                    else:
                        referred_schema = default_schema
                        referred_table = splitted_referred_table[0]
                else:
                    referred_schema, referred_table = foreign_cols[0].split(".")
                fk_relation_obj["_cols"] = local_columns
                fk_relation_obj["ref_table"] = referred_table
                fk_relation_obj["ref_schema"] = referred_schema
                fk_relation_obj["ref_cols"] = foreign_cols[1].replace(")", "").split(",")
                fk_relations.append(fk_relation_obj)

            elif line.startswith('CONSTRAINT'):
                constrain_name, constrain_keys = line.split(" PRIMARY KEY ")
                constrain_name = constrain_name.replace("CONSTRAINT ", "")
                pk_name = constrain_name
                if constrain_keys[-1] == ",":
                    constrain_keys = constrain_keys[0:len(constrain_keys) - 1]
                constrain_keys = constrain_keys.replace("(", "").replace(")", "").split(",")
                for constrain_key in constrain_keys:
                    columns[constrain_key]["is_pk"] = True

            elif line == ')':
                pass
            else:
                col_object = {'name': "", 'type': "", "is_pk": False, "is_fk": False, "enums": None}
                column_name, _type = line.split(" ", 1)
                if _type[-1] == ",":
                    _type = _type[0:len(_type) - 1]
                col_object["name"] = column_name
                if _type.startswith('ENUM'):
                    col_object["type"] = "Enum"
                    col_object["enums"] = _type.replace("ENUM(", "").replace(")", "").replace('"', "").split(",")
                else:
                    col_object["type"] = _type
                columns[column_name] = col_object

        dbinfo[schema_name][table_name] = {
            'pk_name': pk_name,
            'columns': columns,
            "fk_relations": fk_relations
        }

    return dbinfo


def extract_mapped_tables(sql_query: str, db_type: str):
    """
    Extract mapped tables from SQL query
    :param sql_query: query to be parsed
    :param db_type: database type
    :return:
    """
    final_mapping_info = {
        "Schemas": {},
        "Tables": {},
        "Columns": [],
        "Dependencies": {}
    }
    dependencies = {}
    opt_query = sql_query
    ast = parse_one(opt_query, dialect=DatabaseType_mapper[db_type])
    for cte in ast.find_all(exp.CTE):
        dependencies[cte.alias_or_name] = {
            "SchemaTables": {},
            "Tables": set(),
            "ColumnsAlias": set(),
            "Columns": {}
        }

        # get subquery in cte "with name as (...)"

        query = cte.this.sql(DatabaseType_mapper[db_type])
        parsed_query = parse_one(query, dialect=DatabaseType_mapper[db_type])
        for table in parsed_query.find_all(exp.Table):
            dependencies[cte.alias_or_name]["Tables"].add(table.name if table.db == "" else table.db + "." + table.name)

        for column in parsed_query.find_all(exp.Column):
            if not str(column).startswith('"'):  # for cases where col1 == "Martha"
                if column.table in dependencies[cte.alias_or_name]["Columns"]:
                    dependencies[cte.alias_or_name]["Columns"][column.table].add(column.name)
                else:
                    dependencies[cte.alias_or_name]["Columns"][column.table] = {column.name}
        for alias in parsed_query.find_all(exp.Alias):
            dependencies[cte.alias_or_name]["ColumnsAlias"].add(alias.alias)

    for column in ast.find_all(exp.Column):
        # if not str(column).startswith('"'):
        final_mapping_info["Columns"].append(str(column))
    for table in ast.find_all(exp.Table):
        table_name = table.name if table.db == "" else table.db + "." + table.name
        final_mapping_info["Tables"][table.alias] = table_name
    final_mapping_info["Dependencies"] = dependencies
    return final_mapping_info


def find_column_recursive(table_name: str, column_name: str, translations: dict, table_map: dict, db_type: str,
                          column_map={}):
    """
    Searches recursively through translations using the table_map.
    :param table_name: table name to search for
    :param column_name: column name to search for
    :param translations: translation object containing normalized to unnormalied names
    :param table_map: table mapping info for sql query
    :param column_map: cte column mapping from table map used for recursion
    :return:
    """
    splitted_table = table_name.split(".")
    if len(splitted_table) == 1 and splitted_table[0] in table_map["Dependencies"]:  # cte table so
        ## could be juust extracted from only public schema what to do then ???
        search_table = splitted_table[0]
        #
        ## find dependent tables in cte creation
        for new_table in table_map["Dependencies"][search_table]["Tables"]:
            # research with new tables
            return find_column_recursive(new_table, column_name, translations, table_map, db_type,
                                         table_map["Dependencies"][search_table]["Columns"])
    else:
        if len(splitted_table) == 1:
            search_table = splitted_table[0]
            search_schema = get_default_schema(translations, db_type)
        else:
            search_schema, search_table = splitted_table
        if column_name in translations[search_schema]['Tables'][search_table]["Columns"]:
            return translations[search_schema]['Tables'][search_table]["Columns"][column_name]
        else:
            return None  # nochmal checken ??


DatabaseType_mapper = {
    "MySQL": "mysql",
    "PostgreSQL": "postgres",
    "Oracle": "oracle",
    "MsSql": "tsql",
    "SQLite": "sqlite",
    "BigQuery": "bigquery",
    "Redshift": "redshift"
}
Default_Schema_mapper = {
    "MySQL": "mysql",
    "PostgreSQL": "postgres",
    "Oracle": "oracle",
    "MsSql": "tsql",
    "SQLite": "sqlite",
    "BigQuery": "bigquery",
    "Redshift": "redshift"
}


def get_default_schema(translations: dict, db_type: str):
    """
    Extracts default schema name in case the model is not generating it
    :param translations:
    :param db_type:
    :return:
    """
    # Map of each database type to its default schema name
    default_schemas = {
        "MySQL": "mysql",
        "PostgreSQL": "public",
        "Oracle": "SYS",  # You might want "SYSTEM" depending on your setup
        "MsSql": "dbo",
        "SQLite": None,  # SQLite does not have schemas; return None or handle separately
        "BigQuery": None,  # BigQuery uses datasets, handle separately or return None
        "Redshift": "public"
    }
    if db_type == "Oracle":
        if "SYS" not in translations:
            return "SYSTEM"
        else:
            return default_schemas[db_type]
    else:
        return default_schemas[db_type]


def translate_sql_args(query: str, translations: dict, db_type: str) -> str:
    """
    Takes in an sql query that uses normalized names and mappes them to
    their unnormalized counterpart
    :param query: sql query to be translated
    :param translations: translation map containing normalized to unnormalized names
    :param db_type: type of database
    :return:
    """
    identifier_start = '"' if db_type != "MsSql" else '['
    identifier_end = '"' if db_type != "MsSql" else ']'
    default_schema_name = get_default_schema(translations, db_type)

    query = optimize(query, dialect=DatabaseType_mapper[db_type]).sql(DatabaseType_mapper[db_type])
    mapped_table = extract_mapped_tables(query, db_type)
    for column in mapped_table["Columns"]:
        column = column.replace('"', '')
        split_col = column.split(".")
        if len(split_col) == 1:
            continue
        table_alias, column_name = split_col  ## table alias dank libary
        table_schema_split = mapped_table["Tables"][table_alias].split(".")  ## get real table name
        # table is schema.table or just table in case of cte
        new_col_name = column_name
        if len(table_schema_split) == 2:

            schema, table = table_schema_split
            if column_name in translations[schema]['Tables'][table]["Columns"]:
                new_col_name = translations[schema]['Tables'][table]["Columns"][column_name]
        else:
            ## if table name in cte it is a cte table if not assume default public schema and query only uses public
            table = table_schema_split[0]
            if table not in mapped_table["Dependencies"]:
                schema = default_schema_name

                if column_name in translations[schema]['Tables'][table]["Columns"]:
                    new_col_name = translations[schema]['Tables'][table]["Columns"][column_name]
            else:

                if column_name not in mapped_table["Dependencies"][table]["ColumnsAlias"]:
                    search_result = find_column_recursive(table, column_name, translations, mapped_table, db_type, {})
                    if search_result is None:
                        pass
                    else:
                        new_col_name = search_result
        query = query.replace(
            f'{identifier_start}{table_alias}{identifier_end}.{identifier_start}{column_name}{identifier_end}',
            f'{identifier_start}{table_alias}{identifier_end}.{identifier_start}{new_col_name}{identifier_end}')

    for table_alias in mapped_table["Tables"]:
        split_table_name = mapped_table["Tables"][table_alias].split(".")

        if len(split_table_name) == 2 or split_table_name[0] not in mapped_table["Dependencies"]:
            if len(split_table_name) == 2:
                schema, table_name = split_table_name
            else:
                schema = default_schema_name
                table_name = split_table_name[0]
            if table_name in translations[schema]['Tables']:
                true_name_table = translations[schema]['Tables'][table_name]["name"]

                # query = query.replace(f'"{table_alias}"', f'"{true_name_table}"')
                query = query.replace(f'{identifier_start}{table_name}{identifier_end}',
                                      f'{identifier_start}{true_name_table}{identifier_end}')

    return query


def get_proper_naming(_input: str) -> str:
    """
    Transforms a db, schema, table and column name into a proper naming
    :param _input: input name
    :return: normalized name
    """
    return _input.lower().replace(" ", "_").replace("-", "_").replace(".", "_")
