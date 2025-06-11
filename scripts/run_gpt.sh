#!/usr/bin/env bash
set -eu

# --- API and Model Config ---
# api format
PROVIDER="openai" # Options: 'azure' | 'openai'

# llm serve's url, e.g.
# - azure: "https://gcrendpoint.azurewebsites.net/openai/deployments/{MODEL}"
# - deepseek: "https://api.deepseek.com"
BASE_URL="https://api.deepseek.com"

API_KEY=""

# only need to change when use azure serve
API_VERSION="2024-02-01"

# which model your llm serve deployed, e.g.
# - azure: gpt-4, gpt-4-32k, gpt-4-turbo, gpt-35-turbo, GPT35-turbo-instruct
# - aliyun: qwq-plus, qwen-max, qwen3-235b-a22b
# - deepseek platform: deepseek-chat
# - local llm server: deepseek-ai/DeepSeek-R1, Qwen/Qwen3-32B
MODEL="Qwen/Qwen3-32B"

# --- Data and Path Config ---
# eval question json file, depends on your DB type
EVAL_PATH="data/minidev/MINIDEV/mini_dev_sqlite.json" # _sqlite.json, _mysql.json, _postgresql.json

# default sqlite file's path
DB_ROOT_PATH="data/minidev/MINIDEV/dev_databases/"

# output path for the generated SQL queries
DATA_OUTPUT_PATH="exp_result/"

# --- Execution Config ---
# task mode
MODE="mini_dev" # Options: "dev" | "train" | "mini_dev"

# SQL dialect to run
# PLEASE NOTE: You have to setup the database information in table_schema.py
# if you want to run the evaluation script using MySQL or PostgreSQL
SQL_DIALECT="SQLite" # Options: "SQLite" | "PostgreSQL" | "MySQL"

# number of threads to run in parallel, 1 for single thread
NUM_THREADS=6

# use evidence in question json file (to let llm have more information) or not
USE_KNOWLEDGE="True"

# generate cot prompt or not
COT="True"

# how to execute python script, depends on your package manager
EXEC_CMD="uv run" # Options: "uv run" | "conda run -n mini_dev"

function main() {
  echo "ICL setup:"
  echo "  LLM provider:           ${PROVIDER}"
  echo "  Model:                  ${MODEL}"
  echo "  SQL Dialect:            ${SQL_DIALECT}"
  echo "  Eval path:              ${EVAL_PATH}"
  echo "  Output path:            ${DATA_OUTPUT_PATH}"
  echo "  Threads:                ${NUM_THREADS}"
  echo "  Use knowledge:          ${USE_KNOWLEDGE}"
  echo "  With chain of thought:  ${COT}"
  echo ""

  echo "Task will run in 5 seconds. Press Ctrl+C to cancel..."
  for ((i = 5; i > 0; i--)); do
    echo "${i}"
    sleep 1
  done

  echo "Starting to generate perdict sql"
  ${EXEC_CMD} python -u llm/src/gpt_request.py \
    --provider ${PROVIDER} \
    --base_url ${BASE_URL} \
    --api_key ${API_KEY} \
    --api_version ${API_VERSION} \
    --model ${MODEL} \
    --eval_path ${EVAL_PATH} \
    --db_root_path ${DB_ROOT_PATH} \
    --data_output_path ${DATA_OUTPUT_PATH} \
    --mode ${MODE} \
    --sql_dialect ${SQL_DIALECT} \
    --num_threads ${NUM_THREADS} \
    --use_knowledge ${USE_KNOWLEDGE} \
    --chain_of_thought ${COT}
}

main "$@"
