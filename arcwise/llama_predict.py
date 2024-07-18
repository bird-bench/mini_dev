import asyncio
from collections import defaultdict
from contextlib import aclosing
from functools import partial
import json
import random
import click
import litellm
import os
import requests
from tqdm import tqdm

from .ddl import get_database_ddl
from .typedefs import BIRDQuestion, Database, LlamaPredictions
from .utils import coro, load_database_metadata, load_questions, run_with_concurrency

N_SAMPLES = 5


@click.command()
@click.option("--questions-file", help="Path to questions JSON", required=True)
@click.option("--output-file", help="Path to output file", required=True)
@click.option("--metadata-file", help="Path to JSON metadata", required=True)
@click.option("--model", help="Model identifier", required=True)
@click.option("--concurrency", default=2, help="Number of questions to evaluate concurrently")
@coro
async def main(
    questions_file: str,
    output_file: str,
    metadata_file: str,
    model: str,
    concurrency: int,
) -> None:
    if custom_base_url := os.environ.get("OPENAI_API_BASE"):
        # Allow for warmup time
        while True:
            # Note: will still throw an exception if the domain is non-existent
            response = requests.get(custom_base_url, timeout=600)
            if response.ok or response.status_code == 404:
                break
            print(f"Got {response.status_code} from {custom_base_url}, retrying...")
            await asyncio.sleep(1)

    questions = load_questions(questions_file)
    metadata = load_database_metadata(metadata_file)

    callables = [
        partial(process_question, question, metadata[question.db_id], model)
        for question in questions
        if not question.llama_predictions
    ]

    def _write_output() -> None:
        with open(output_file, "w") as f:
            json.dump([q.model_dump(exclude_none=True) for q in questions], f, indent=2)

    async with aclosing(run_with_concurrency(callables, concurrency)) as results:
        with tqdm(total=len(callables)) as pbar:
            async for _ in results:
                pbar.update(1)
                if pbar.n % 10 == 0:
                    _write_output()

    _write_output()


async def process_question(
    question: BIRDQuestion,
    db: Database,
    model: str,
) -> None:
    # TODO implement basic retrieval pass
    schema = get_database_ddl(db)
    question.filtered_schema = schema

    try:
        response = await litellm.acompletion(
            model=model,
            messages=SCHEMA_PREDICTION_PROMPT
            + [
                {
                    "role": "user",
                    "content": f"""Given the database:
<schema>
{question.filtered_schema}
</schema>
{question.question.strip()}
{'Context: ' + question.evidence if question.evidence else ''}""".strip(),
                },
            ],
            n=N_SAMPLES,
            temperature=1.0,
            custom_llm_provider="openai",
        )
        input_column_descriptions = defaultdict(list)
        output_types_by_shape = defaultdict(list)
        for choice in response.choices:  # type: ignore
            lines = choice.message.content.strip().splitlines()  # type: ignore
            if "Input Columns" not in lines:
                continue

            input_columns_line = lines.index("Input Columns")
            if output_types := _parse_output_types(lines[1:input_columns_line]):
                output_types_by_shape[tuple(o.type for o in output_types)].append(output_types)

            last_desc = None
            for line in lines[input_columns_line + 1 :]:
                if line.startswith("--"):
                    last_desc = line[2:].strip()
                elif "::" in line:
                    col, table = line.split("::")
                    input_column_descriptions[table + "." + col].append(last_desc)

        majority_output = None
        for outputs in output_types_by_shape.values():
            if len(outputs) > N_SAMPLES / 2:
                majority_output = random.choice(outputs)

        # Sort by most common input columns
        final_input_columns = [
            LlamaPredictions.InputColumn(
                column=col,
                description=random.choice(descs),
                votes=len(descs),
            )
            for col, descs in sorted(
                input_column_descriptions.items(),
                key=lambda x: -len(x[1]),
            )
        ]

        question.llama_predictions = LlamaPredictions(
            # NOTE: Output prediction is ignored if we couldn't obtain majority
            output_types=majority_output or [],
            input_columns=final_input_columns,
        )
    except Exception as err:
        print(
            "Error getting prediction for question:",
            question.model_dump_json(include={"db_id", "question"}),
        )
        print(f"Exception message: {err}")


def _parse_output_types(lines: list[str]) -> list[LlamaPredictions.OutputType]:
    output_types = []
    last_desc = None
    for line in lines:
        if line.startswith("--"):
            last_desc = line[2:].strip()
        elif type_ := line.strip():
            if not last_desc or type_ not in {"real", "integer", "text", "date", "datetime"}:
                return []
            output_types.append(LlamaPredictions.OutputType(type=type_, description=last_desc))
            last_desc = None
    return output_types


SCHEMA_PREDICTION_PROMPT = [
    {
        "role": "system",
        "content": """Given a SQL database and question, please determine a list of "Output Types" and "Input Columns" required to answer the question.
Before each list item, write a `--` line comment explaining why it is needed, citing the user's question when possible.
Output types should be one of: real, integer, text, date
Input columns should be formatted without quotes as: column_name::table_name
Ensure that the output types provide exactly the information needed to answer the question and nothing more or less.""",
    },
    {
        "role": "user",
        "content": """Given the database:
<schema>
CREATE TABLE sales (
sale_date date,
product_id integer,
quantity real
);
CREATE TABLE prices (
price_date date,
product_id integer,
price real
);
CREATE TABLE products (
product_id integer,
product_name text
);
</schema>
What was the average price by product name in January 2024?""",
    },
    {
        "role": "assistant",
        "content": """Output Types
-- The product name for the average price
text
-- 'average price of carrots in January 2024' for the product name
real
Input Columns
-- The question asks for the 'average price'. We should aggregate the price column in prices
price::prices
-- To filter for prices 'in January 2024', we should use the price_date column in prices
price_date::prices
-- To filter for prices 'of carrots', we need to use the product_id column to join against products
product_id::prices
-- Join key for product_id in prices
product_id::products
-- Finally, we can group by the product_name column in products
product_name::products""",
    },
]


if __name__ == "__main__":
    main()
