from dataclasses import dataclass
from functools import cache
from typing import Literal

import sqlglot
import sqlglot.expressions
from sqlglot import Dialect
from sqlglot.dialects.dialect import NormalizationStrategy

from ..typedefs import ColumnType


@dataclass
class SchemaColumn:
    name: str
    db_type: str | None
    data_type: ColumnType | None
    description: str | None


@cache
def get_sqlglot_dialect(dialect: str) -> Dialect:
    return Dialect[dialect]()

@cache
def get_dialect_keywords(dialect: Dialect) -> set[str]:
    # SQLGlot treats "ORDER BY", "GROUP BY", etc as a single keyword
    return {part for keyword in dialect.tokenizer.KEYWORDS for part in keyword.split()}


def should_quote_identifier(name: str, *, dialect: str | Dialect) -> bool | None:
    if isinstance(dialect, str):
        dialect = get_sqlglot_dialect(dialect)

    # Alarmingly, SQLGlot's built-in quoting logic does not check for keywords.
    if name.upper() in get_dialect_keywords(dialect):
        return True

    # TODO: For full correctness we need to record whether or not the identifier was quoted
    # in the source data warehouse (in INFORMATION_SCHEMA).
    # As a heuristic, look for mixed-case identifiers in case-sensitive dialects.
    if dialect.normalization_strategy is not NormalizationStrategy.CASE_INSENSITIVE:
        has_upper = False
        has_lower = False
        for c in name:
            has_upper |= c.isupper()
            has_lower |= c.islower()
        if has_upper and has_lower:
            return True

    # Use the standard dialect quoting logic
    return None


def create_schema_ddl(
    quoted_name: str,
    entity_type: Literal["table", "view"],
    columns: list[SchemaColumn],
    select_sql: str | None,
    description: str | None,
    dialect: str,
) -> str:
    """
    Returns a CREATE TABLE or CREATE VIEW statement which incorporates the provided descriptions/source query.
    (Not designed for actual execution, but more for AI prompting.)
    """
    schema = ""
    if description:
        schema = "\n".join(["-- " + line for line in description.splitlines()]) + "\n"
    schema += f"CREATE {entity_type.upper()} {quoted_name}"
    if columns:
        column_lines = []
        for idx, column in enumerate(columns):
            # Description will be added as a comment above the column line
            description = column.description or ""

            sql_type = column.db_type
            if not sql_type:
                match column.data_type:
                    case ColumnType.Number:
                        # TODO: would be nice to differentiate integer types
                        sg_type = sqlglot.expressions.DataType.build("NUMERIC")
                    case ColumnType.Date:
                        sg_type = sqlglot.expressions.DataType.build("DATE")
                    case ColumnType.Time:
                        sg_type = sqlglot.expressions.DataType.build("DATETIME")
                    case ColumnType.Boolean:
                        sg_type = sqlglot.expressions.DataType.build("BOOLEAN")
                    case ColumnType.String:
                        sg_type = sqlglot.expressions.DataType.build("STRING")
                    # Ignore other types for now
                    case _:
                        continue
                sql_type = sg_type.sql(dialect=dialect)

            if entity_type == "view":
                # NOTE: there is no way to properly annotate types on views, so add it to the description
                description += ("\n" if description else "") + "type: " + sql_type
            if description:
                description = "\t-- " + description.replace("\n", "\n\t-- ") + "\n"

            column_name = sqlglot.column(
                column.name,
                quoted=should_quote_identifier(column.name, dialect=dialect),
            ).sql(dialect=dialect)
            comma = "," if idx < len(columns) - 1 else ""
            if entity_type == "table":
                column_line = f"{description}\t{column_name} {sql_type}{comma}"
            else:
                column_line = f"{description}\t{column_name}{comma}"
            column_lines.append(column_line)

        schema += " (\n" + "\n".join(column_lines) + "\n)"
    if select_sql:
        schema += f" AS {select_sql}"
    return schema + ";"
