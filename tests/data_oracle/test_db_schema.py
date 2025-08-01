from app.data_oracle.db_schema import Column, Table, Database, Foreign_Key_Relation, Schema


def test_db_apply_filter():
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
    scanned_db.apply_table_name_filter({"pub": ["Persons", "T1"]})
    scanned_db.apply_table_name_filter({"pub": ["Test3", "Test4"], "pubmore": ["Test3", "Test4"]})
    scanned_db.apply_table_regex_filter({"pub": "Test[0-9]+", "pubmore": "Test[0-9]+"})
    assert ["pub", "pubmore"] == [x.name for x in scanned_db.get_schemas()]
    assert {"pub": set(["Test2", "T1"]), "pubmore": set(["Test2"])} == {schema.name: set(schema.get_filtered_tables())
                                                                        for schema in
                                                                        scanned_db.get_schemas()}


def test_db_release_filter():
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
    scanned_db.apply_table_name_filter({"pub": ["Persons", "T1"]})
    scanned_db.apply_table_name_filter({"pub": ["Test3", "Test4"], "pubmore": ["Test3", "Test4"]})
    scanned_db.apply_table_regex_filter({"pub": "Test[0-9]+", "pubmore": "Test[0-9]+"})

    scanned_db.release_filters()

    assert {"pub": set(), "pubmore": set()} == {schema.name: set(schema.get_filtered_tables())
                                                for schema in
                                                scanned_db.get_schemas()}


def test_db_get_schemas():
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

    scanned_db.apply_schema_name_filter(["pub"])
    assert ["pubmore"] == [schema.name for schema in scanned_db.get_schemas()]


def test_filter_columns():
    column_list = [
        Column("Col1", "INTEGER", True, True),
        Column("Col2", "INTEGER"),
        Column("Col3", "INTEGER"),
        Column("Test1", "INTEGER"),
        Column("Col4", "INTEGER")
    ]
    table_list = [
        Table("T1", None, column_list, "Table", []),
        Table("T2", None, column_list + [Column("Test2", "INTEGER", True, True)], "Table", [])
    ]
    schema_list = [Schema("pub", table_list), Schema("pubmore", table_list)]
    scanned_db = Database("test")  #
    scanned_db.register_schemas(schema_list)

    name_filter = {"pub": {
        "T1": ["Col1", "Col2", "Col3"]
    }}

    regex_filter = {"pub": {
        "T2": "Test[0-9]+"
    }}
    scanned_db.apply_column_name_filter(name_filter)
    scanned_db.apply_column_regex_filter(regex_filter)

    assert {'pub': {'T1': ['Col1', 'Test1', 'Col4'],
                    'T2': ['Col1', 'Col2', 'Col3', 'Col4', 'Test2']},
            'pubmore': {'T1': ['Col1', 'Test1', 'Col4'],
                        'T2': ['Col1', 'Col2', 'Col3', 'Col4', 'Test2']}} == {
               schema.name: {table.name: [col.name for col in table.get_cols()] for table in schema.get_tables()}
               for schema in
               scanned_db.get_schemas()
           }


def test_cached_layout():
    column_list = [
        Column("Col1", "INTEGER", True, True),
        Column("Col2", "INTEGER"),
        Column("Col3", "INTEGER"),
        Column("Test1", "INTEGER"),
        Column("Col4", "INTEGER")
    ]
    table_list = [
        Table("T1", None, column_list, "Table", []),
        Table("T2", None, column_list + [Column("Test2", "INTEGER", True, True)], "Table", [Foreign_Key_Relation(**{
            "_cols": ["Col1"], "ref_table": "T1", "ref_schema": "pub", "ref_cols": ["Col1", "Col2"]
        })])
    ]
    schema_list = [Schema("pub", table_list), Schema("pubmore", table_list)]
    scanned_db = Database("test")  #
    scanned_db.register_schemas(schema_list)

    cached_layout = scanned_db.return_code_repr_schema()

    comparison_db = Database("test2")
    comparison_db.reload_from_cache(cached_layout)

    assert scanned_db.return_code_repr_schema() == comparison_db.return_code_repr_schema()


def test_cached_layout_string():
    layout = """CREATE SCHEMA public;

CREATE TABLE public.albums(
id INTEGER,
title VARCHAR(160),
artist_id INTEGER,
PRIMARY KEY (id),
FOREIGN KEY (artist_id) REFERENCES public.artists(id)
)

CREATE TABLE public.artists(
id INTEGER,
name VARCHAR(120),
PRIMARY KEY (id)
)

CREATE TABLE public.customers(
id INTEGER,
first_name VARCHAR(40),
last_name VARCHAR(20),
company VARCHAR(80),
address VARCHAR(70),
city VARCHAR(40),
state VARCHAR(40),
country VARCHAR(40),
postal_code VARCHAR(10),
phone VARCHAR(24),
fax VARCHAR(24),
email VARCHAR(60),
support_rep_id INTEGER,
PRIMARY KEY (id),
FOREIGN KEY (support_rep_id) REFERENCES public.employees(id)
)

CREATE TABLE public.employees(
id INTEGER,
last_name VARCHAR(20),
first_name VARCHAR(20),
title VARCHAR(30),
reports_to INTEGER,
birth_date TIMESTAMP,
hire_date TIMESTAMP,
address VARCHAR(70),
city VARCHAR(40),
state VARCHAR(40),
country VARCHAR(40),
postal_code VARCHAR(10),
phone VARCHAR(24),
fax VARCHAR(24),
email VARCHAR(60),
PRIMARY KEY (id),
FOREIGN KEY (reports_to) REFERENCES public.employees(id)
)

CREATE TABLE public.genres(
id INTEGER,
name VARCHAR(120),
PRIMARY KEY (id)
)

CREATE TABLE public.invoice_lines(
id INTEGER,
invoice_id INTEGER,
track_id ENUM("Manufacturing","Speciality Products","Corporate","Research & Development"),
unit_price NUMERIC(10, 2),
quantity INTEGER,
PRIMARY KEY (id),
FOREIGN KEY (invoice_id) REFERENCES public.invoices(id),
FOREIGN KEY (track_id) REFERENCES public.tracks(id)
)

CREATE TABLE public.invoices(
id INTEGER,
customer_id INTEGER,
invoice_date TIMESTAMP,
billing_address VARCHAR(70),
billing_city VARCHAR(40),
billing_state VARCHAR(40),
billing_country VARCHAR(40),
billing_postal_code VARCHAR(10),
total NUMERIC(10, 2),
PRIMARY KEY (id),
FOREIGN KEY (customer_id) REFERENCES public.customers(id)
)

CREATE TABLE public.media_types(
id INTEGER,
name VARCHAR(120),
PRIMARY KEY (id)
)

CREATE TABLE public.playlist_tracks(
playlist_id INTEGER,
track_id INTEGER,
CONSTRAINT PK_PlaylistTrack PRIMARY KEY (playlist_id,track_id),
FOREIGN KEY (playlist_id) REFERENCES public.playlists(id),
FOREIGN KEY (track_id) REFERENCES public.tracks(id)
)

CREATE TABLE public.playlists(
id INTEGER,
name VARCHAR(120),
PRIMARY KEY (id)
)

CREATE TABLE public.tracks(
id INTEGER,
name VARCHAR(200),
album_id INTEGER,
media_type_id INTEGER,
genre_id INTEGER,
composer VARCHAR(220),
milliseconds INTEGER,
bytes INTEGER,
unit_price NUMERIC(10, 2),
PRIMARY KEY (id),
FOREIGN KEY (album_id) REFERENCES public.albums(id,car_id),
FOREIGN KEY (genre_id,album_id) REFERENCES public.genres(id),
FOREIGN KEY (media_type_id) REFERENCES public.media_types(id)
)"""
    comparison_db = Database("test2")
    comparison_db.reload_from_cache(layout)
    assert layout == comparison_db.return_code_repr_schema()


def test_proper_naming_layout():
    column_list = [
        Column("Col1 SPACE", "INTEGER", True, True),
        Column("Col2_UNDERSCORE", "INTEGER"),
        Column("Col3.DOT", "INTEGER"),
        Column("Test1", "INTEGER"),
        Column("Col4", "INTEGER")
    ]
    table_list = [
        Table("T1", None, column_list, "Table", []),
        Table("T2", None, column_list + [Column("Test2", "INTEGER", True, True)], "Table", [Foreign_Key_Relation(**{
            "_cols": ["Col1 SPACE"], "ref_table": "T1", "ref_schema": "pub", "ref_cols": ["Col1", "Col2_UNDERSCORE"]
        })])
    ]
    schema_list = [Schema("pub", table_list), Schema("pubmore", table_list)]
    scanned_db = Database("test")  #
    scanned_db.register_schemas(schema_list)

    cached_layout = scanned_db.return_code_repr_schema_normalized()

    normalized_layout = """CREATE SCHEMA pub;
CREATE SCHEMA pubmore;

CREATE TABLE pub.t1(
col1_space INTEGER,
col2_underscore INTEGER,
col3_dot INTEGER,
test1 INTEGER,
col4 INTEGER,
PRIMARY KEY (col1_space)
)

CREATE TABLE pub.t2(
col1_space INTEGER,
col2_underscore INTEGER,
col3_dot INTEGER,
test1 INTEGER,
col4 INTEGER,
test2 INTEGER,
PRIMARY KEY (col1_space),
FOREIGN KEY (col1_space) REFERENCES pub.t1(col1,col2_underscore)
)

CREATE TABLE pubmore.t1(
col1_space INTEGER,
col2_underscore INTEGER,
col3_dot INTEGER,
test1 INTEGER,
col4 INTEGER,
PRIMARY KEY (col1_space)
)

CREATE TABLE pubmore.t2(
col1_space INTEGER,
col2_underscore INTEGER,
col3_dot INTEGER,
test1 INTEGER,
col4 INTEGER,
test2 INTEGER,
PRIMARY KEY (col1_space),
FOREIGN KEY (col1_space) REFERENCES pub.t1(col1,col2_underscore)
)"""

    assert normalized_layout == cached_layout


def test_proper_translations_map():
    column_list = [
        Column("Col1 SPACE", "INTEGER", True, True),
        Column("Col2_UNDERSCORE", "INTEGER"),
        Column("Col3.DOT", "INTEGER"),
        Column("Test1", "INTEGER"),
        Column("Col4", "INTEGER")
    ]
    table_list = [
        Table("T1 SPACE", None, column_list, "Table", []),
        Table("T2.DOT", None, column_list + [Column("Test2", "INTEGER", True, True)], "Table", [Foreign_Key_Relation(**{
            "_cols": ["Col1 SPACE"], "ref_table": "T1", "ref_schema": "pub", "ref_cols": ["Col1", "Col2_UNDERSCORE"]
        })])
    ]
    schema_list = [Schema("pub", table_list), Schema("pubmore", table_list)]
    scanned_db = Database("test")  #
    scanned_db.register_schemas(schema_list)

    real_translation_map = {'pub': {'name': 'pub', 'Tables': {'t1_space': {'name': 'T1 SPACE',
                                                                           'Columns': {'col1_space': 'Col1 SPACE',
                                                                                       'col2_underscore': 'Col2_UNDERSCORE',
                                                                                       'col3_dot': 'Col3.DOT',
                                                                                       'test1': 'Test1',
                                                                                       'col4': 'Col4'}},
                                                              't2_dot': {'name': 'T2.DOT',
                                                                         'Columns': {'col1_space': 'Col1 SPACE',
                                                                                     'col2_underscore': 'Col2_UNDERSCORE',
                                                                                     'col3_dot': 'Col3.DOT',
                                                                                     'test1': 'Test1', 'col4': 'Col4',
                                                                                     'test2': 'Test2'}}}}, 'pubmore'
                            : {'name': 'pubmore', 'Tables': {'t1_space': {'name': 'T1 SPACE',
                                                                          'Columns': {'col1_space': 'Col1 SPACE',
                                                                                      'col2_underscore': 'Col2_UNDERSCORE',
                                                                                      'col3_dot': 'Col3.DOT',
                                                                                      'test1': 'Test1',
                                                                                      'col4': 'Col4'}},
                                                             't2_dot': {'name': 'T2.DOT',
                                                                        'Columns': {'col1_space': 'Col1 SPACE',
                                                                                    'col2_underscore': 'Col2_UNDERSCORE',
                                                                                    'col3_dot': 'Col3.DOT',
                                                                                    'test1': 'Test1', 'col4': 'Col4',
                                                                                    'test2': 'Test2'}}}}}

    assert real_translation_map == scanned_db.translations_map
