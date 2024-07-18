import subprocess

import sqlglot
import sqlglot.expressions as exp
from pydantic import BaseModel
from sqlglot.optimizer.normalize_identifiers import normalize_identifiers
from sqlglot.optimizer.optimizer import optimize
from sqlglot.optimizer.scope import traverse_scope

from .typedefs import Table


class SQLReferences(BaseModel):
    tables: list[str]
    columns: list[str]
    output_schema: list[str]


def extract_sql_references(
    db_path: str,
    tables: list[Table],
    query: str,
    query_runtime_types: bool = True,
) -> SQLReferences:
    # Parse the query using sqlglot
    parsed = sqlglot.parse_one(query, dialect="sqlite")
    parsed = normalize_identifiers(parsed, dialect="sqlite")
    parsed = optimize(
        parsed,
        schema={table.name: {col.name: col.type for col in table.columns} for table in tables},
        dialect="sqlite",
    )

    table_names_lower = {table.name.lower(): table for table in tables}
    ref_tables = []
    for table in parsed.find_all(exp.Table):
        if (
            orig_table := table_names_lower.get(table.name.lower())
        ) and table.name not in ref_tables:
            ref_tables.append(orig_table.name)

    # Extract columns
    ref_columns = []
    for scope in traverse_scope(parsed):
        for col in scope.columns:
            if not col.table:
                continue

            source = scope.sources.get(col.table)
            if isinstance(source, exp.Table):
                orig_table = table_names_lower[source.name.lower()]
                orig_col_name = next(
                    orig_col.name
                    for orig_col in orig_table.columns
                    if orig_col.name.lower() == col.name.lower()
                )
                q = f"{orig_table.name}.{orig_col_name}"
                if q not in ref_columns:
                    ref_columns.append(q)

    while isinstance(parsed, (exp.Except, exp.Intersect, exp.Union)):
        parsed = parsed.left

    assert isinstance(parsed, exp.Select), f"Expected SELECT, got {type(parsed)}"
    output_schema = [
        exp.DataType.build(expr.type.this).sql(dialect="sqlite").lower()
        for expr in parsed.expressions
    ]
    assert output_schema, f"No output schema for {parsed}"

    if query_runtime_types and ("unknown" in output_schema or "null" in output_schema):
        # Wrap each selected column in a typeof() and execute it
        sql = (
            sqlglot.select(
                *[sqlglot.func("typeof", sqlglot.column(col.alias)) for col in parsed.expressions]
            )
            .from_(parsed.subquery())
            .limit(1)
            .sql(dialect="sqlite")
        )
        # More reliable than using built-in SQLite3 (and we can apply a timeout for bad queries)
        output = subprocess.check_output(["sqlite3", "-csv", db_path, sql], timeout=20.0)
        output_schema = output.decode().strip().split(",")

    return SQLReferences(tables=ref_tables, columns=ref_columns, output_schema=output_schema)


if __name__ == "__main__":
    print(extract_sql_references("/dev/null", [], "SELECT 1, 'a', 1.0"))
