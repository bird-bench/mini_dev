import asyncio
import csv
import re
from io import StringIO

import sqlglot
import sqlglot.expressions as exp
from pydantic import BaseModel, Field

from .utils import SQLContext

SQLScalar = str | int | float | bool | None


class ExecuteSQLToolArguments(BaseModel):
    query_description: str = Field(description="An explanation of the purpose of this query")
    query_identifier: str = Field(
        description="A short SQL identifier name that describes the query"
    )
    table_identifiers: list[str] = Field(
        description="A list of tables or prior exec_result_ids to use in the query"
    )
    sql: str


class ExecuteSQLToolResult(BaseModel):
    error: str | None = None
    columns: list[str] | None = None
    rows: list[list[SQLScalar]] | None = None
    exec_result_id: str | None = None
    sql: str | None = None


EXECUTE_SQL_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_sql",
        "description": "Executes a SQL query",
        "parameters": ExecuteSQLToolArguments.model_json_schema(),
    },
}


async def execute_sql_tool(
    arguments: ExecuteSQLToolArguments,
    previous_sql_queries: dict[str, str],
    sql_context: SQLContext,
) -> tuple[str, ExecuteSQLToolResult]:
    exec_result_id = _get_unique_str(
        re.sub("[^A-Za-z0-9_]", "_", arguments.query_identifier).lower(),
        list(previous_sql_queries.keys()),
    )
    sql = arguments.sql.strip().rstrip(";")
    sg_query = sqlglot.parse_one(sql, dialect=sql_context.dialect).transform(_lint_sql)
    assert isinstance(sg_query, exp.Query), "Only SELECT statements are supported"
    for table in arguments.table_identifiers:
        if previous_sql := previous_sql_queries.get(table):
            if sg_query.ctes:
                # Needs to be prepended, as existing CTEs may reference `cte_name`
                new_cte = exp.CTE(
                    alias=table, this=sqlglot.parse_one(previous_sql, dialect=sql_context.dialect)
                )
                sg_query.ctes.insert(0, new_cte)
            else:
                sg_query = sg_query.with_(
                    alias=table, as_=previous_sql, dialect=sql_context.dialect
                )

    sql = sg_query.sql(dialect=sql_context.dialect)
    if (
        arguments.query_identifier.startswith("final_answer")
        and arguments.table_identifiers
        and (division_nodes := [node for node in sg_query.find_all(exp.Div)])
    ):
        # Do some sanity checks on the final query
        for division_node in division_nodes:
            _check_tables_used_for_division(division_node, sg_query)

    try:
        columns, rows = await execute_sql(sql, sql_context)
        tool_result = ExecuteSQLToolResult(
            exec_result_id=exec_result_id,
            rows=rows,
            columns=columns,
            sql=sql,
        )
        gpt_result = _get_gpt_result(
            rows=rows,
            columns=columns,
            exec_result_id=exec_result_id,
        )
    except Exception as exc:
        error_message = str(exc)
        tool_result = ExecuteSQLToolResult(
            sql=sql,
            exec_result_id=exec_result_id,
            error=error_message,
        )
        gpt_result = "Error executing query: " + error_message
    return gpt_result, tool_result


EXECUTE_SQL_ROWS_BYTE_LIMIT = 512


def _get_gpt_result(
    rows: list[list[SQLScalar]],
    columns: list[str],
    exec_result_id: str,
) -> str:
    tsv_preview = StringIO()
    writer = csv.writer(tsv_preview, delimiter="\t", lineterminator="\n")
    writer.writerow(columns)
    for i, row in enumerate(rows):
        if tsv_preview.tell() > EXECUTE_SQL_ROWS_BYTE_LIMIT:
            tsv_preview.write(f"```\n{len(rows) - i} more rows hidden")
            break
        writer.writerow(row)

    return f"""exec_result_id: {exec_result_id}
row_count: {len(rows)}
```tsv
{tsv_preview.getvalue()}"""


def _get_unique_str(proposed_base_str: str, others: list[str]) -> str:
    final_str = proposed_base_str
    i = 1
    lowercase_others = set(s.lower() for s in others)
    while final_str.lower() in lowercase_others:
        final_str = f"{proposed_base_str}_{i}"
        i += 1
    return final_str


async def execute_sql(
    sql: str, sql_context: SQLContext, timeout: float = 30.0
) -> tuple[list[str], list[list[SQLScalar]]]:
    assert sql_context.dialect == "sqlite"
    rows = await asyncio.wait_for(_execute_sqlite(sql, sql_context), timeout)
    if not len(rows):
        # TODO: is there a way to force SQLite to always return the header?
        raise Exception("Query returned no results")
    return rows[0], list(rows[1:])  # type: ignore


async def _execute_sqlite(sql: str, sql_context: SQLContext) -> list[list[str]]:
    process = None
    try:
        process = await asyncio.create_subprocess_exec(
            "sqlite3",
            "-csv",
            "-header",
            sql_context.db_url,
            sql,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"SQLite error: {stderr.decode()}")

        return list(csv.reader(StringIO(stdout.decode()), delimiter=","))
    except asyncio.CancelledError:
        if process:
            process.terminate()
        raise


def _lint_sql(node: exp.Expression) -> exp.Expression:
    # If there are any asc ORDER BYs, make sure that nulls_first is False
    if isinstance(node, exp.Ordered):
        if not node.args.get("desc"):
            node.args["nulls_first"] = False

    return node


# If a division mixes column references from two CTEs (or a CTE and the query itself),
# assert that the two scopes have the same set of tables.
# If they don't, it's a sign that the numerator & denominator operate on different quantities/units.
def _check_tables_used_for_division(node: exp.Div, sg_query: exp.Query):
    # Find all tables used in each CTE
    ctes_to_tables: dict[str, set[str]] = {
        t.alias or t.name: {t.name for t in t.this.find_all(exp.Table)}
        for t in sg_query.find_all(exp.CTE)
    }
    if not ctes_to_tables:
        return

    # Find all tables used in the root query scope
    root_tables = {t.name for t in sg_query.find_all(exp.Table) if t.name not in ctes_to_tables}

    numerator_tables = _find_tables_used(node.left, ctes_to_tables, root_tables)
    denominator_tables = _find_tables_used(node.right, ctes_to_tables, root_tables)
    if numerator_tables != denominator_tables:
        raise RuntimeError(f"""
Division `{node.sql()}` is operating on different units.
The numerator and denominator must be derived from the same set of tables, e.g.

```sql
SELECT
  CAST(
    COUNT(DISTINCT
      CASE
        WHEN t2.is_valid THEN t1.id
      END
    ) AS REAL
  ) * 100 / COUNT(DISTINCT t1.id) percent
FROM table1 AS t1
INNER JOIN table2 AS t2 ON t1.id = t2.id
```

Please rework the query and try again.
""")


# Find all table names used in column "scopes" for a given node
def _find_tables_used(
    node: exp.Expression, cte_table_refs: dict[str, set[str]], root_table_refs: set[str]
) -> set[str]:
    result = set()
    for column in node.find_all(exp.Column):
        result.update(cte_table_refs.get(column.table) or root_table_refs)
    return result
