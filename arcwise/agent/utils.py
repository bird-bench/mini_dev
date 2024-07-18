import csv
from dataclasses import dataclass
from io import StringIO
from typing import Any

from litellm.types.completion import ChatCompletionMessageParam
from ..typedefs import Database


@dataclass
class EvaluationResult:
    predicted_sql: str
    predicted_result: list[list[Any]] | str
    message_log: list[ChatCompletionMessageParam]
    ex_match: bool | None = None
    golden_result: list[list[Any]] | None = None

    def dump(self) -> dict[str, Any]:
        return {
            "ex_match": self.ex_match,
            "predicted_sql": self.predicted_sql,
            "predicted_result": (
                to_tsv(self.predicted_result)
                if isinstance(self.predicted_result, list)
                else self.predicted_result
            ),
            "golden_result": to_tsv(self.golden_result) if self.golden_result else None,
            "message_log": self.message_log,
        }


@dataclass
class SQLContext:
    dialect: str
    db_url: str
    db_metadata: dict[str, Database]
    model: str


def to_tsv(data: list[list[Any]]) -> str:
    with StringIO() as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerows(data)
        return f.getvalue().strip("\n")
