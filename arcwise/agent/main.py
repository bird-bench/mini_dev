import json
import logging
import random
from typing import Any, Coroutine

import click
from litellm import asyncio
from tqdm import tqdm

from .run_agent import evaluate_question
from .utils import EvaluationResult, SQLContext
from ..typedefs import BIRDQuestion
from ..utils import coro, load_database_metadata, load_questions


@click.command()
@click.option("--db-path", help="Path to SQLite databases", required=True)
@click.option("--metadata-file", help="Path to metadata.json file", required=True)
@click.option(
    "--questions-file",
    help="Path to questions JSON",
    required=True,
)
@click.option("--question-ids", default="", help="Comma-separated list of question IDs to pick")
@click.option("--model", default="gpt-4o", help="LLM to use")
@click.option("--concurrency", default=2, help="Number of questions to evaluate concurrently")
@click.option("--log-file", default="agent.log", help="File for logging output")
@click.option("--report-file", default="report.json", help="Output path for final report")
@click.option("--resume", is_flag=True, help="Resume from last report", default=False)
@coro
async def main(
    db_path: str,
    metadata_file: str,
    questions_file: str,
    question_ids: str,
    model: str,
    concurrency: int,
    log_file: str,
    report_file: str,
    resume: bool,
) -> None:
    # Remove default console handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        filename=log_file,
        filemode="a",
        format="%(asctime)s - [%(levelname)s] %(name)s - %(message)s",
        level=logging.INFO,
    )

    question_id_list = list(map(int, question_ids.split(","))) if question_ids else None
    questions = load_questions(questions_file, question_id_list)
    db_metadata = load_database_metadata(metadata_file)

    semaphore = asyncio.Semaphore(concurrency)

    async def _concurrency_wrapper(
        aw: Coroutine[Any, Any, tuple[int, BIRDQuestion, EvaluationResult]],
    ) -> tuple[int, BIRDQuestion, EvaluationResult]:
        async with semaphore:
            return await aw

    # Randomly shuffle questions for smoother progress/accuracy
    shuffled = list(enumerate(questions))
    random.shuffle(shuffled)

    results = []
    existing_questions = set()
    if resume:
        try:
            with open(report_file) as f:
                results = json.load(f)
        except FileNotFoundError:
            print("--resume specified but no report file found")
            return
        existing_questions = {r["question_id"] for r in results}

    tasks = [
        asyncio.create_task(
            _concurrency_wrapper(
                evaluate_question(
                    index,
                    q,
                    SQLContext(
                        dialect="sqlite",
                        db_url=db_path + f"/{q.db_id}/{q.db_id}.sqlite",
                        db_metadata=db_metadata,
                        model=model,
                    ),
                )
            )
        )
        for index, q in shuffled
        if q.question_id not in existing_questions
    ]
    total = len(results)
    ex_correct = len([r for r in results if r["ex_match"]])
    exceptions = 0
    pbar = tqdm(asyncio.as_completed(tasks), total=len(tasks))
    for result_task in pbar:
        index, question, result = await result_task
        total += 1
        if result.ex_match:
            ex_correct += 1
        elif isinstance(result.predicted_result, BaseException):
            exceptions += 1
        pbar.set_description(f"Accuracy: {ex_correct / total:.2%}")
        results.append(
            {
                "index": index,
                **question.model_dump(exclude_unset=True),
                **result.dump(),
            }
        )
        if total % 10 == 0:
            _write_report(results, report_file)

    print(f"Final EX score: {ex_correct / total:.2%}")
    print(f"Exceptions: {exceptions}")
    _write_report(results, report_file)


def _write_report(results: list[dict[str, Any]], report_file: str) -> None:
    results.sort(key=lambda x: x["index"])
    with open(report_file, "w") as f:
        json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
