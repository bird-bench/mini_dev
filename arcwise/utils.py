import asyncio
import json
from typing import AsyncGenerator, Awaitable, Callable, Sequence, TypeVar


from .typedefs import Database, BIRDQuestion


# Make an async function runnable synchronously (i.e. main())
def coro(f):  # type: ignore
    def wrapper(*args, **kwargs):  # type: ignore
        return asyncio.run(f(*args, **kwargs))

    return wrapper


T = TypeVar("T")


async def run_with_concurrency(
    callables: Sequence[Callable[[], Awaitable[T]]],
    concurrency: int,
) -> AsyncGenerator[tuple[int, T], None]:
    semaphore = asyncio.Semaphore(concurrency)

    async def _concurrency_wrapper(index: int, aw: Callable[[], Awaitable[T]]) -> tuple[int, T]:
        async with semaphore:
            return index, await aw()

    tasks = [
        asyncio.create_task(_concurrency_wrapper(index, c)) for index, c in enumerate(callables)
    ]
    for result in asyncio.as_completed(tasks):
        yield await result


def load_questions(
    questions_file: str, question_ids: list[int] | None = None
) -> list[BIRDQuestion]:
    with open(questions_file) as f:
        questions_raw = json.load(f)
        assert isinstance(questions_raw, list), f"{questions_file} must contain a JSON list"

    return [
        BIRDQuestion.model_validate(q)
        for q in questions_raw
        if question_ids is None
        or (question_id := q.get("question_id")) is None
        or question_id in question_ids
    ]


def load_database_metadata(
    metadata_file: str,
) -> dict[str, Database]:
    with open(metadata_file) as f:
        metadata_raw = json.load(f)
        assert isinstance(metadata_raw, list), f"{metadata_file} must contain a JSON list"

    return {db["name"]: Database.model_validate(db) for db in metadata_raw}
