#!/usr/bin/env bash
set -eu

# --- User Modify Variables ---
# main data path
DATA_PATH="data/minidev/MINIDEV"

# default sqlite file's path
DB_ROOT_PATH="${DATA_PATH}/dev_databases/"

# how many cpus to run the eval
NUM_CPUS=3

# maximum seconds to execute sql
META_TIME_OUT=30.0

# how to execute python script, depends on your package manager
EXEC_CMD="uv run" # Options: "uv run" | "conda run -n mini_dev"

# kind of DB you use
SQL_DIALECT="SQLite" # Options: "SQLite" | "PostgreSQL" | "MySQL"

# your predict sql json path, which may generate by llm before
# so make it same as your DATA_OUTPUT_PATH in run_gpt.sh
PREDICTED_SQL_PATH="exp_result/predict_mini_dev_deepseek-chat_cot_SQLite.json"

# define the output log path, which has same basename as your predict sql json
OUTPUT_LOG_PATH="eval_result/$(basename "$PREDICTED_SQL_PATH" .json).txt"

# --- DO NOT CHANGE BELOW ---
EX_SCRIPT="evaluation/evaluation_ex.py"
R_VES_SCRIPT="evaluation/evaluation_ves.py"
F1_SCRIPT="evaluation/evaluation_f1.py"

case $SQL_DIALECT in
"SQLite")
  diff_json_path="${DATA_PATH}/mini_dev_sqlite.json"
  ground_truth_path="${DATA_PATH}/mini_dev_sqlite_gold.sql"
  ;;
"PostgreSQL")
  diff_json_path="${DATA_PATH}/mini_dev_postgresql.json"
  ground_truth_path="${DATA_PATH}/mini_dev_postgresql_gold.sql"
  ;;
"MySQL")
  diff_json_path="${DATA_PATH}/mini_dev_mysql.json"
  ground_truth_path="${DATA_PATH}/mini_dev_mysql_gold.sql"
  ;;
*)
  echo "Invalid SQL dialect: $SQL_DIALECT"
  exit 1
  ;;
esac
# --- DO NOT CHANGE ABOVE ---

function eval() {
  local eval_name="${1}"
  local python_script="${2}"

  echo "Starting to compare with knowledge for ${1}"
  ${EXEC_CMD} python -u ${python_script} \
    --db_root_path "${DB_ROOT_PATH}" \
    --predicted_sql_path "${PREDICTED_SQL_PATH}" \
    --ground_truth_path "${ground_truth_path}" \
    --num_cpus "${NUM_CPUS}" \
    --output_log_path "${OUTPUT_LOG_PATH}" \
    --diff_json_path "${diff_json_path}" \
    --meta_time_out "${META_TIME_OUT}" \
    --sql_dialect "${SQL_DIALECT}"
}

function conform() {
  local evals="${1}"
  local countdown=5

  echo "Evaluation ${evals} will run next. Press Ctrl+C to cancel..."
  for ((i = countdown; i > 0; i--)); do
    echo "${i}"
    sleep 1
  done
}

function main() {
  local param="${1:-0}"

  echo "Evaluation setup:"
  echo "  SQL Dialect:            ${SQL_DIALECT}"
  echo "  Predicted SQL Path:     ${PREDICTED_SQL_PATH}"
  echo "  Differential JSON Path: ${diff_json_path}"
  echo "  Ground Truth Path:      ${ground_truth_path}"
  echo "  Output Log Path:        ${OUTPUT_LOG_PATH}"
  echo "  CPUs:                   ${NUM_CPUS}"
  echo "  Timeout:                ${META_TIME_OUT}s"
  echo ""

  echo "You provided the parameter: ${param:-(none)}"

  case "$param" in
  "0" | "all" | "")
    conform "EX, R-VES, Soft F1-Score"
    eval "EX" "${EX_SCRIPT}"
    eval "R-VES" "${R_VES_SCRIPT}"
    eval "Soft F1-Score" "${F1_SCRIPT}"
    ;;
  "1" | "ex")
    conform "EX"
    eval "EX" "${EX_SCRIPT}"
    ;;
  "2" | "ves")
    conform "R-VES"
    eval "R-VES" "${R_VES_SCRIPT}"
    ;;
  "3" | "f1")
    conform "Soft F1-Score"
    eval "Soft F1-Score" "${F1_SCRIPT}"
    ;;
  *)
    echo "Error: Invalid parameter: '${param}'"
    echo "Usage: $0 [0|all|1|ex|2|ves|3|f1]"
    echo "  0 or all or None: Run all evaluations(EX, R-VES, F1), default"
    echo "  1 or ex:          Run EX evaluation only"
    echo "  2 or ves:         Run R-VES evaluation only"
    echo "  3 or f1:          Run F1 evaluation only"
    exit 1
    ;;
  esac
}

main "$@"
