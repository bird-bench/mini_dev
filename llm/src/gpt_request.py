#!/usr/bin/env python3
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from tqdm import tqdm

from llm_client import LLMClient
from prompt import generate_combined_prompts_one


@dataclass
class Config:
    """
    Encapsulates all script configurations.
    """
    # API and Model Config
    provider: str # 'azure' | 'openai'
    base_url: str
    api_key: str
    api_version: str
    model: str

    # Data and Path Config
    eval_path: str
    db_root_path: str
    data_output_path: str

    # Execution Config
    mode: str = "dev"
    use_knowledge: bool = False
    chain_of_thought: bool = False
    num_threads: int = 3
    sql_dialect: str = "SQLite"

@dataclass
class Task:
    """
    Represents a single task for the worker to process.
    """
    index: int
    question: str
    db_path: str
    prompt: str


def prepare_tasks(config: Config):
    """
    Prepares the list of tasks to be processed.
    """
    with open(config.eval_path, 'r') as f:
        eval_data = json.load(f)

    tasks = []
    for i, data in enumerate(eval_data):
        db_path = Path(config.db_root_path )/ data["db_id"] / f"{data['db_id']}.sqlite"
        knowledge = data.get("evidence") if config.use_knowledge else None

        prompt = generate_combined_prompts_one(
            db_path=db_path,
            question=data["question"],
            sql_dialect=config.sql_dialect,
            knowledge=knowledge,
        )
        tasks.append(Task(index=i, question=data["question"], db_path=db_path, prompt=prompt))

    return tasks

def process_task(task: Task, client: LLMClient) -> tuple[str, int]:
    """
    Worker function to process a single task.
    """
    response_text = client.ask(task.prompt)
    db_id = Path(task.db_path).stem
    sql_result = f"{response_text}\t----- bird -----\t{db_id}"
    print(f"Processed {task.index}th question: {task.question}")

    return sql_result, task.index

def generate_sql_file(results: list, output_path: Path):
    """
    Saves the generated SQL results to a JSON file, sorted by index.
    """
    if not results:
        return

    results.sort(key=lambda x: x[1])
    output_dict = {i: sql for i, (sql, _) in enumerate(results)}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(output_dict, f, indent=4)
    print(f"Successfully saved results to {output_path}")

def load_config():
    args_parser = argparse.ArgumentParser()
    # API and Model Config
    args_parser.add_argument("--provider", type=str, default="openai")
    args_parser.add_argument("--base_url", type=str, required=True)
    args_parser.add_argument("--api_key", type=str, required=True)
    args_parser.add_argument("--api_version", type=str, default="")
    args_parser.add_argument(
        "--model", type=str, required=True, default="code-davinci-002"
    )

    # Data and Path Config
    args_parser.add_argument("--eval_path", type=str, default="")
    args_parser.add_argument("--db_root_path", type=str, default="")
    args_parser.add_argument("--data_output_path", type=str)

    # Execution Config
    args_parser.add_argument("--mode", type=str, default="dev")
    args_parser.add_argument("--sql_dialect", type=str, default="SQLite")
    args_parser.add_argument("--num_threads", type=int, default=3)
    args_parser.add_argument("--use_knowledge", type=str, default="False")
    args_parser.add_argument("--chain_of_thought", type=str)

    args = args_parser.parse_args()

    return Config(
        provider=args.provider,
        base_url=args.base_url,
        api_key=args.api_key,
        api_version=args.api_version,
        model=args.model,
        eval_path=args.eval_path,
        db_root_path=args.db_root_path,
        data_output_path=args.data_output_path,
        mode=args.mode,
        sql_dialect=args.sql_dialect,
        num_threads=args.num_threads,
        use_knowledge=args.use_knowledge,
        chain_of_thought=args.chain_of_thought,
    )

def main():
    cfg = load_config()
    llm = LLMClient(
        provider=cfg.provider,
        model=cfg.model,
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        api_version=cfg.api_version
    )
    tasks = prepare_tasks(cfg)
    all_responses = []
    
    with ThreadPoolExecutor(max_workers=cfg.num_threads) as executor:
        future_to_task = {executor.submit(process_task, task, llm): task for task in tasks}

        for future in tqdm(as_completed(future_to_task), total=len(tasks), desc="Generating SQL"):
            try:
                result = future.result()
                all_responses.append(result)
            except Exception as e:
                print(f"A task generated an exception: {e}")

    cot_suffix = "_cot" if cfg.chain_of_thought else ""
    output_file =(
        Path(cfg.data_output_path) /
        f"predict_{cfg.mode}_{cfg.model}{cot_suffix}_{cfg.sql_dialect}.json"
    )

    generate_sql_file(results=all_responses, output_path=output_file)

    print(
        f"successfully collect results from {cfg.model} for {cfg.mode} evaluation; "
        f"SQL dialect {cfg.sql_dialect} Use knowledge: {cfg.use_knowledge}; "
        f"Use COT: {cfg.chain_of_thought}"
    )


if __name__ == "__main__":
    main()
