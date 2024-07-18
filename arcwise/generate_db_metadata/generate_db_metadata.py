import json
import os
import pathlib
import re
import sqlite3
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pandas as pd
from cachetools import cached
from fastapi.encoders import jsonable_encoder
from litellm.cost_calculator import completion_cost
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
from tqdm import tqdm

from .utils import SchemaColumn, create_schema_ddl
from ..typedefs import BIRDDatabase, ColumnInfo, ColumnStatistics, Database, ForeignKey, Table
import litellm

RELATIONSHIPS = {
    (True, True): "one-to-one",
    (True, False): "one-to-many",
    (False, True): "many-to-one",
    (False, False): "many-to-many",
}
SQLITE_DIALECT = sqlite_dialect()

@cached(key=lambda x, y, _, __: f"{x}/{y}", cache={})
def get_column_stats(
    db_path: str, db_id: str, table_names: list[str], db_column_names: list[tuple[int, str]]
) -> dict[str, list[ColumnStatistics]]:
    sqlite_path = pathlib.Path(db_path) / f"{db_id}/{db_id}.sqlite"
    result = {}

    def process_table(table_info):
        i, table_name = table_info
        try:
            column_names = [col for table_index, col in db_column_names if table_index == i]
            with sqlite3.connect(sqlite_path) as conn:
                cursor = conn.cursor()

                # Construct a single query to get all stats for all columns
                query = f"""
                SELECT
                    COUNT(*) AS row_count,
                    {', '.join([f'''
                    SUM(CASE WHEN "{col}" IS NULL THEN 1 ELSE 0 END) AS null_count_{col_i},
                    COUNT(DISTINCT "{col}") AS distinct_count_{col_i},
                    (
                        SELECT JSON_GROUP_ARRAY(val)
                        FROM (
                            SELECT "{col}" AS val, COUNT(*)
                            FROM "{table_name}"
                            WHERE "{col}" IS NOT NULL
                            GROUP BY 1
                            ORDER BY 2 DESC
                            LIMIT 10
                        )
                    ) AS most_common_{col_i},
                    JSON_ARRAY(MIN("{col}"), MAX("{col}")) AS histogram_{col_i}
                    ''' for col_i, col in enumerate(column_names)])}
                FROM "{table_name}"
                """

                cursor.execute(query)
                result_row = cursor.fetchone()

                row_count = int(result_row[0])
                table_stats = []

                for i, column in enumerate(column_names):
                    null_count, distinct_count, most_common, histogram = result_row[i * 4 + 1 : i * 4 + 5]
                    null_count = int(null_count or 0)
                    distinct_count = int(distinct_count or 0)
                    null_fraction = null_count / row_count if row_count else 1.0
                    distinct_percent = distinct_count / row_count if row_count else 0.0

                    stats = ColumnStatistics(
                        table_name=table_name,
                        row_count=row_count,
                        null_fraction=null_fraction,
                        distinct_count=distinct_count,
                        distinct_percent=distinct_percent,
                        most_common_vals=json.loads(most_common),
                        histogram=json.loads(histogram) if histogram != "[null,null]" else None,
                    )
                    table_stats.append(stats)

                return table_name, table_stats
        except Exception as err:
            print(f"Error reading {db_id} / {table_name}: {err}")
            raise

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_table, (i, table_name)) for i, table_name in enumerate(table_names)]
        for future in futures:
            table_name, table_stats = future.result()
            result[table_name] = table_stats

    return result


@cached(key=lambda x, y, _: f"{x}/{y}", cache={})
def get_column_types(db_path: str, db_id: str, table_names: list[str]) -> dict[str, dict[str, tuple[str, str]]]:
    sqlite_path = pathlib.Path(db_path) / f"{db_id}/{db_id}.sqlite"
    result = {}
    with sqlite3.connect(sqlite_path) as conn:
        cursor = conn.cursor()
        for table_name in table_names:
            # Get the SQLite table schema
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            schema = cursor.fetchall()
            result[table_name] = {col[1].lower(): (col[1], col[2].lower()) for col in schema}
    return result


def normalize_identifier(name: str) -> str:
    return name


def approx_eq(a, b, tol=1e-6):
    return abs(a - b) < tol


def read_table_description(db_path: str, db_id: str, table_name: str):
    descriptions = None
    full_path = pathlib.Path(db_path) / f"{db_id}/database_description/{table_name}.csv"
    for encoding in ["utf-8", "latin1", "ISO-8859-1", "cp1252"]:
        try:
            descriptions = pd.read_csv(full_path, encoding=encoding)
            break
        except:
            pass
    if descriptions is None:
        raise Exception(f"Could not read {full_path}")
    assert (
        len(descriptions.columns) == 5
    ), f"{db_id} / {table_name}.csv has {len(descriptions.columns)} columns (expected 5)"
    descriptions.fillna("", inplace=True)
    return descriptions


def _trunc(v: Any):
    if isinstance(v, str) and len(v) > 100:
        return v[:100] + "…"
    return v


def _column_json(c: ColumnInfo):
    col_dict = {
        "name": normalize_identifier(c.name),
        "original_name": c.original_name,
        "description": c.description,
        "value_description": c.value_description,
        "sample_values": [_trunc(v) for v in c.sample_values] if c.sample_values else None,
        "unique_count": c.unique_count,
        "min": _trunc(c.min_value),
        "max": _trunc(c.max_value),
    }
    return json.dumps({k: v for k, v in col_dict.items() if v is not None}, separators=(",", ":"))


def _normalize_for_json(name: str):
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


def quote_identifier(name: str):
    ip = SQLITE_DIALECT.identifier_preparer
    if name in ip.reserved_words or name[0] in ip.illegal_initial_characters or not ip.legal_characters.match(name):
        return ip.quote_identifier(name)
    return name


async def run(db_path: str, output_schemas_path: str, tables_json: str, output_metadata_file: str):
    with open(tables_json) as f:
        tables = [BIRDDatabase.model_validate(item) for item in json.load(f)]
    output_databases = []

    # Get column stats
    for item in tqdm(tables):
        db_id = item.db_id
        table_names = item.table_names_original
        db_column_names = item.column_names_original
        table_column_stats = get_column_stats(db_path, db_id, table_names, db_column_names)
        db_column_stats = sum(table_column_stats.values(), [])

        table_column_names = defaultdict(list)
        for table_index, column_name in db_column_names:
            if table_index >= 0:
                table_name = table_names[table_index]
                column_index = len(table_column_names[table_name])
                table_column_names[table_name].append(column_name)

        foreign_keys_by_table = defaultdict(list)
        for from_col_index, to_col_index in item.foreign_keys:
            from_table_index, from_column_name = db_column_names[from_col_index]
            to_table_index, to_column_name = db_column_names[to_col_index]
            from_table_name = table_names[from_table_index]
            to_table_name = table_names[to_table_index]
            from_col_stats = db_column_stats[from_col_index - 1]
            to_col_stats = db_column_stats[to_col_index - 1]

            from_unique = approx_eq(from_col_stats.distinct_percent + from_col_stats.null_fraction, 1)
            to_unique = approx_eq(to_col_stats.distinct_percent + to_col_stats.null_fraction, 1)

            foreign_keys_by_table[from_table_name].append(
                (
                    from_column_name,
                    ForeignKey(
                        reference_table=normalize_identifier(to_table_name),
                        reference_column=normalize_identifier(to_column_name),
                        relationship=RELATIONSHIPS[(from_unique, to_unique)],
                    ),
                )
            )
            foreign_keys_by_table[to_table_name].append(
                (
                    normalize_identifier(to_column_name),
                    ForeignKey(
                        reference_table=normalize_identifier(from_table_name),
                        reference_column=normalize_identifier(from_column_name),
                        relationship=RELATIONSHIPS[(to_unique, from_unique)],
                    ),
                )
            )

        primary_keys_by_table = defaultdict(list)
        for pkey in item.primary_keys:
            if not isinstance(pkey, list):
                stats = db_column_stats[pkey - 1]
                assert approx_eq(
                    stats.distinct_percent + stats.null_fraction, 1
                ), f"pkey not unique: {db_column_names[pkey]} {stats}"
                pkey = [pkey]
            for i in pkey:
                table_index, column_name = db_column_names[i]
                primary_keys_by_table[table_names[table_index]].append(normalize_identifier(column_name))

        output_tables = []
        for table_index, table_name in enumerate(table_names):
            # entity_table = next((e for e in entities if e.name == normalize_identifier(table_name)), None)
            column_stats = table_column_stats[table_name]
            column_names = table_column_names[table_name]
            assert len(column_stats) == len(column_names), f"{column_names} missing stats: {len(column_stats)}"
            # assert len(entity_table.columns) == len(column_names), f"{table_name} columns don't match DB"
            rowcount = column_stats[0].row_count

            descriptions = read_table_description(db_path, db_id, table_name)
            description_rows = list(descriptions.itertuples(index=False))
            description_by_name = {normalize_identifier(row[0].strip()): row for row in description_rows}

            table_fkeys = foreign_keys_by_table[table_name]

            output_columns = []
            for column_name, stats in zip(column_names, column_stats):
                column_name = normalize_identifier(column_name)
                assert column_name in description_by_name, f"{db_id} / {table_name}: no description for {column_name}"
                _, orig_col_name, description, col_type, value_description = description_by_name[column_name]
                column_fkeys = [fk for (col, fk) in table_fkeys if col == column_name]
                output_columns.append(
                    ColumnInfo(
                        name=column_name,
                        original_name=orig_col_name.strip() if orig_col_name else None,
                        # type=entity_table.columns[i]["db_type"],
                        type=col_type.strip().lower(),
                        description=description.strip() if description else None,
                        value_description=value_description.strip() if value_description else None,
                        foreign_keys=column_fkeys,
                        null_fraction=stats.null_fraction,
                        unique_count=int(stats.distinct_count),
                        unique_fraction=stats.distinct_percent,
                        sample_values=(stats.most_common_vals or stats.histogram or [])[:10],
                        min_value=min((stats.histogram or []) + (stats.most_common_vals or []), default=None),
                        max_value=max((stats.histogram or []) + (stats.most_common_vals or []), default=None),
                    )
                )

            output_tables.append(
                Table(
                    name=table_name,
                    row_count=rowcount,
                    primary_key=primary_keys_by_table[table_name],
                    columns=output_columns,
                )
            )

        output_databases.append(Database(name=db_id, tables=output_tables))

    # Get column types
    for db in output_databases:
        table_names = [table.name for table in db.tables]
        column_types = get_column_types(db_path, db.name, table_names)
        for table in db.tables:
            for column in table.columns:
                if not (type_info := column_types[table.name].get(column.name.lower())):
                    print(f"Missing type info for {db.name}.{table.name}.{column.name}")
                    continue
                real_name, real_type = type_info
                column.name = real_name
                column.type = real_type

    # Save cleaned metadata
    tables_cleaned_path = tables_json.replace(".json", "_cleaned.json")
    with open(tables_cleaned_path, "w") as f:
        f.write(json.dumps(jsonable_encoder(output_databases), indent=2))


    # Generate AI descriptions
    total_cost = 0.0
    pbar = tqdm(output_databases)
    for item in pbar:
        for table in item.tables:
            if table.ai_description:
                continue

            pbar.set_description(f"{item.name}.{table.name} (${total_cost:.2f})")

            system_prompt = """You are an expert, detail-oriented, data analyst.

Your task is to call `describe_table` with high-quality descriptions based on user-provided tables.
Do not respond with anything else.

For each column, provide as concise of a description as you can given the following constraints:
- Omit the description if the column name is self-explanatory.
- If a column is similar to a previous column, its description should be 'See [previous column]'.
- IMPORTANT: if value_description lists sample_values, explains the meanings of certain values, or mentions that the values are not useful, this information MUST be preserved in the final description.
- If the values appear to follow a consistent format or pattern, describe the pattern.
- If the values are numerical, describe the range of values.
- Provide a few representative sample values if it is not obvious. Put single quotes around string values. If there are less than 5, include them all.

The ordering of the columns should match their original ordering. Only use information provided in the column JSON.
At the end, provide a table_description__ (but do not mention the exact row count.)"""
            tool = {
                "type": "function",
                "function": {
                    "name": "describe_table",
                    "description": "See instructions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            **{
                                _normalize_for_json(c.name): {
                                    "type": "string",
                                    "description": f"Description for column {c.name}",
                                }
                                for c in table.columns
                            },
                            "table_description__": {
                                "type": "string",
                                "description": "Brief 1-line table description",
                            },
                        },
                        "additionalProperties": False,
                        "required": [_normalize_for_json(c.name) for c in table.columns] + ["table_description__"],
                    },
                },
            }
            column_json = "\n".join([_column_json(c) for c in table.columns])
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f'Describe this SQLite table named "{table.name}" with {table.row_count} rows and the following columns:\n{column_json}',
                },
            ]
            result = await litellm.acompletion(
                model="claude-3-5-sonnet-20240620",
                custom_llm_provider="anthropic",
                messages=messages,
                tools=[tool],
                tool_choice={"type": "function", "function": {"name": "describe_table"}},
                temperature=0.0,
                max_retries=3,
            )
            total_cost += completion_cost(completion_response=result, messages=messages)
            descriptions = json.loads(result.choices[0].message.tool_calls[0].function.arguments)  # type: ignore

            table_description = descriptions["table_description__"]
            if table_description:
                table_description += "\n"
            table_description += f"{table.row_count} rows"
            if table.primary_key:
                table_description += f", primary key: ({', '.join(table.primary_key)})"
            table.ai_description = table_description

            for column in table.columns:
                ai_description = descriptions.get(_normalize_for_json(column.name)) or ""
                if ai_description:
                    ai_description += "\n"
                ai_description += (
                    f"Stats: {column.null_fraction*100:.3g}% null {column.unique_fraction*100:.3g}% unique"
                )
                if column.foreign_keys:
                    if ai_description:
                        ai_description += "\n"
                    ai_description += "Foreign keys: " + ", ".join(
                        [
                            f"{quote_identifier(fk.reference_table)}.{quote_identifier(fk.reference_column)} ({fk.relationship})"
                            for fk in column.foreign_keys
                        ]
                    )
                column.ai_description = ai_description

    with open(output_metadata_file, "w") as f:
        f.write(json.dumps(jsonable_encoder(output_databases), indent=2))

    # Generate schema files
    for db in output_databases:
        ddls = [
            create_schema_ddl(
                quote_identifier(table.name),
                entity_type="table",
                columns=[
                    SchemaColumn(column.name, column.type, None, column.ai_description) for column in table.columns
                ],
                select_sql=None,
                description=table.ai_description,
                dialect="sqlite",
            ).replace("\t", "")
            for table in db.tables
        ]
        output_schema_file = pathlib.Path(f"{output_schemas_path}/{db.name}.sql")
        os.makedirs(os.path.dirname(output_schema_file), exist_ok=True)
        with open(output_schema_file, "w") as f:
            f.write("\n".join(ddls))
