# 🚀 LiveSQLBench-Base-Lite
*A dynamic, **contamination‑free** benchmark for evaluating LLMs on complex, real‑world ****text‑to‑SQL**** tasks.*

[🌐 Website](https://livesqlbench.ai) • [📄 Paper (coming soon)](https://arxiv.org) • [💻 GitHub](https://github.com/bird-bench/livesqlbench)

Maintained by the **🦜 [BIRD Team @ HKU](https://bird-bench.github.io)** & **☁️ [Google Cloud](https://cloud.google.com/)**

## Dataset Access
Checkout our [Hugging Face Page](https://huggingface.co/datasets/birdsql/livesqlbench-base-lite-sqlite) for easy access to the LiveSQLBench-Base-Lite-SQLite dataset.

🔐 To avoid data leakage by auto-crawling, certain fields (e.g., `sol_sql`, `test_cases`, `external_knowledge`) are excluded from the public dataset `livesqlbench_data_sqlite.jsonl`. For the full dataset, please email: **[📧 bird.bench25@gmail.com](mailto:bird.bench25@gmail.com)** with subject tag `[livesqlbench-base-lite-SQLite GT&Test Cases]`, which will be sent automatically.

## 🎯 Current Release: LiveSQLBench-Base-Lite-SQLite
We are pleased to release a **SQLite version** of **LiveSQLBench-Base-Lite**, extending from PostgreSQL to SQLite dialect to **improve accessibility** — SQLite requires no server setup and runs locally. This release features **18 end-user level databases** with **270** tasks (180 SELECT-only, 90 Management tasks), **HKB-JSON** and **JSON operations in SQL** for trial.

Beyond SQL and test case translation, we **carefully adapted 20+ user queries** to align with SQLite's database engine characteristics. For example, since SQLite doesn't support custom functions, we modified queries to either return specific scenario values or utilize views (e.g., `CREATE VIEW AS ...`) to maintain query complexity while ensuring compatibility.

## 📚 Project Structure
```
mini_dev/
├── live_sql_bench_sqlite/
│   ├── database/                # SQLite databases
│   ├── evaluation/              # Evaluation scripts
│   ├── utils/                   # Utility scripts for prompt generation and post-processing
│   ├── prompts/                 # Prompt templates
│   ├── README.md                # This file
```

## 📦 Usage
### Inference
Use the following script to generate the baseline prompt for the SQLite version of LiveSQLBench-Base-Lite:
```bash
cd utils
data_path="xxx/livesqlbench_data_sqlite.jsonl"
assistant_prompt_path="xxx/assistant_sqlite.jsonl" # Replace with your desired output path
data_path_base="xxx/database" # Replace with your database path
python xxx/prompt_generator.py \
    --data_path $data_path \
    --prompt_path $assistant_prompt_path \
    --prompt_type "assistant" \
    --data_path_base $data_path_base
```

The generated jsonl file will contain a `prompt` field. Then you can use your favorite LLM to generate SQL queries based on the provided prompt. 

### 🛠️ Process
After you generate SQL queries using the prompts, you can use the following script to postprocess the generated SQL queries (assume the input is a jsonl file with a `response` field):
```bash
cd utils
input_path="xxx/generated_sql.jsonl" # Replace with your generated SQL file path
output_path="xxx/post_processed_sql.jsonl" # Replace with your desired output path
python xxx/post_process_baseline.py --input_path $input_path --output_path $output_path
```

## 📊 Evaluation
Now we can evaluate the generated SQL queries against the SQLite databases. Use the following script to evaluate the post-processed SQL queries:
```bash
cd evaluation
# # You need to modify the JSONL location or use the HuggingFace dataset in the evaluation.py file
jsonl_file="xxx/post_processed_sql.jsonl" # Replace with your desired output path
python wrapper_evaluation_sqlite.py --jsonl_file $jsonl_file
```