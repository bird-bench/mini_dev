import sqlite3
import pymysql
import psycopg2

db_table_map = {
    "debit_card_specializing": [
        "customers",
        "gasstations",
        "products",
        "transactions_1k",
        "yearmonth",
    ],
    "student_club": [
        "major",
        "member",
        "attendance",
        "budget",
        "event",
        "expense",
        "income",
        "zip_code",
    ],
    "thrombosis_prediction": ["Patient", "Examination", "Laboratory"],
    "european_football_2": [
        "League",
        "Match",
        "Player",
        "Player_Attributes",
        "Team",
        "Team_Attributes",
    ],
    "formula_1": [
        "circuits",
        "seasons",
        "races",
        "constructors",
        "constructorResults",
        "constructorStandings",
        "drivers",
        "driverStandings",
        "lapTimes",
        "pitStops",
        "qualifying",
        "status",
        "results",
    ],
    "superhero": [
        "alignment",
        "attribute",
        "colour",
        "gender",
        "publisher",
        "race",
        "superpower",
        "superhero",
        "hero_attribute",
        "hero_power",
    ],
    "codebase_community": [
        "posts",
        "users",
        "badges",
        "comments",
        "postHistory",
        "postLinks",
        "tags",
        "votes",
    ],
    "card_games": [
        "cards",
        "foreign_data",
        "legalities",
        "rulings",
        "set_translations",
        "sets",
    ],
    "toxicology": ["molecule", "atom", "bond", "connected"],
    "california_schools": ["satscores", "frpm", "schools"],
    "financial": [
        "district",
        "account",
        "client",
        "disp",
        "card",
        "loan",
        "order",
        "trans",
    ],
}


def nice_look_table(column_names: list, values: list):
    rows = []
    # Determine the maximum width of each column
    widths = [
        max(len(str(value[i])) for value in values + [column_names])
        for i in range(len(column_names))
    ]

    # Print the column names
    header = "".join(
        f"{column.rjust(width)} " for column, width in zip(column_names, widths)
    )
    # print(header)
    # Print the values
    for value in values:
        row = "".join(f"{str(v).rjust(width)} " for v, width in zip(value, widths))
        rows.append(row)
    rows = "\n".join(rows)
    final_output = header + "\n" + rows
    return final_output


def generate_schema_prompt_sqlite(db_path, num_rows=None):
    # extract create ddls
    """
    :param root_place:
    :param db_name:
    :return:
    """
    full_schema_prompt_list = []
    conn = sqlite3.connect(db_path)
    # Create a cursor object
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    schemas = {}
    for table in tables:
        if table == "sqlite_sequence":
            continue
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='{}';".format(
                table[0]
            )
        )
        create_prompt = cursor.fetchone()[0]
        schemas[table[0]] = create_prompt
        if num_rows:
            cur_table = table[0]
            if cur_table in ["order", "by", "group"]:
                cur_table = "`{}`".format(cur_table)

            cursor.execute("SELECT * FROM {} LIMIT {}".format(cur_table, num_rows))
            column_names = [description[0] for description in cursor.description]
            values = cursor.fetchall()
            rows_prompt = nice_look_table(column_names=column_names, values=values)
            verbose_prompt = "/* \n {} example rows: \n SELECT * FROM {} LIMIT {}; \n {} \n */".format(
                num_rows, cur_table, num_rows, rows_prompt
            )
            schemas[table[0]] = "{} \n {}".format(create_prompt, verbose_prompt)

    for k, v in schemas.items():
        full_schema_prompt_list.append(v)

    schema_prompt = "\n\n".join(full_schema_prompt_list)

    return schema_prompt


def connect_mysql():
    # Open database connection
    # Connect to the database"
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",
        database="BIRD",
        unix_socket="/tmp/mysql.sock",
        # port=3306,
    )
    return db


def format_mysql_create_table(table_name, columns_info):
    lines = []
    lines.append(f"CREATE TABLE {table_name}\n(")

    primary_key_defined = False

    for col in columns_info:
        column_name, data_type, nullable, key, _, _ = col

        sql_type = str.upper(data_type)

        null_type = "not null" if nullable == "NO" else "null"
        primary_key_part = (
            "primary key" if "PRI" in key and not primary_key_defined else ""
        )
        primary_key_defined = True if "PRI" in key else primary_key_defined
        column_line = (
            f"    `{column_name}` {sql_type} {null_type} {primary_key_part},".strip()
        )
        lines.append(column_line)
    lines[-1] = lines[-1].rstrip(",")
    lines.append(");")
    return "\n".join(lines)


def format_postgresql_create_table(table_name, columns_info):
    lines = [f"CREATE TABLE {table_name}\n("]
    for i, (column_name, data_type, is_nullable) in enumerate(columns_info):
        null_status = "NULL" if is_nullable == "YES" else "NOT NULL"
        postgres_data_type = data_type.upper()
        column_line = f"    `{column_name}` {postgres_data_type} {null_status}"
        if i < len(columns_info) - 1:
            column_line += ","
        lines.append(column_line)

    lines.append(");")
    return "\n".join(lines)


def generate_schema_prompt_mysql(db_path):
    db = connect_mysql()
    cursor = db.cursor()
    db_name = db_path.split("/")[-1].split(".sqlite")[0]
    tables = [table for table in db_table_map[db_name]]
    schemas = {}
    for table in tables:
        cursor.execute(f"DESCRIBE BIRD.{table}")
        raw_schema = cursor.fetchall()
        pretty_schema = format_mysql_create_table(table, raw_schema)
        schemas[table] = pretty_schema
    schema_prompt = "\n\n".join(schemas.values())
    db.close()
    return schema_prompt


def connect_postgresql():
    # Open database connection
    # Connect to the database
    db = psycopg2.connect(
        "dbname=BIRD user=root host=localhost password=YOUR_PASSWORD port=5432"
    )
    return db


def generate_schema_prompt_postgresql(db_path):
    db = connect_postgresql()
    cursor = db.cursor()
    db_name = db_path.split("/")[-1].split(".sqlite")[0]
    tables = [table for table in db_table_map[db_name]]
    schemas = {}
    for table in tables:
        cursor.execute(
            f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{table}';
            """
        )
        raw_schema = cursor.fetchall()
        pretty_schema = format_postgresql_create_table(table, raw_schema)
        schemas[table] = pretty_schema
    schema_prompt = "\n\n".join(schemas.values())
    db.close()
    return schema_prompt


def generate_schema_prompt(sql_dialect, db_path=None, num_rows=None):
    if sql_dialect == "SQLite":
        return generate_schema_prompt_sqlite(db_path, num_rows)
    elif sql_dialect == "MySQL":
        return generate_schema_prompt_mysql(db_path)
    elif sql_dialect == "PostgreSQL":
        return generate_schema_prompt_postgresql(db_path)
    else:
        raise ValueError("Unsupported SQL dialect: {}".format(sql_dialect))
