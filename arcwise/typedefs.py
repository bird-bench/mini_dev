from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


class ForeignKey(BaseModel):
    reference_table: str
    reference_column: str
    relationship: str


class ColumnInfo(BaseModel):
    name: str
    original_name: str | None
    type: str
    ai_description: str | None = None
    description: str | None
    value_description: str | None
    foreign_keys: list[ForeignKey]
    null_fraction: float
    unique_count: int
    unique_fraction: float
    sample_values: list[Any]
    min_value: Any
    max_value: Any


class Table(BaseModel):
    name: str
    ai_description: str | None = None
    row_count: int
    primary_key: list[str]
    columns: list[ColumnInfo]


class Database(BaseModel):
    name: str
    tables: list[Table]


@dataclass
class ColumnStatistics:
    table_name: str
    row_count: int
    null_fraction: float
    distinct_count: int
    distinct_percent: float
    most_common_vals: list[Any] | None = None
    histogram: list[Any] | None = None


class BIRDDatabase(BaseModel):
    db_id: str
    table_names_original: list[str]
    column_names_original: list[tuple[int, str]]  # (table_index, column_name)
    primary_keys: list[list[int] | int]  # index into column_names_original
    foreign_keys: list[tuple[int, int]]  # index into column_names_original
