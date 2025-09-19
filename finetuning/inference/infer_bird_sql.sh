#!/usr/bin/env bash
set -euo pipefail

########################
# User configs
########################
MODEL_PATH="/path/to/your/model-or-checkpoint"  
PROMPT_JSONL="/path/to/dev_or_minidev_prompts.jsonl"  # provided dev or minidev set prompts
OUT_DIR="./outputs/vllm_infer"                   
GPU="0,1"                                        

BATCH_SIZE=50
MAX_LEN=15000
TEMP=0.0

########################
# Prepare
########################
mkdir -p "${OUT_DIR}"
base="$(basename "${PROMPT_JSONL}" .jsonl)"
RAW_OUT="${OUT_DIR}/${base}_raw.jsonl"
FINAL_OUT="${OUT_DIR}/${base}_final.json"

echo "[Info] Model   : ${MODEL_PATH}"
echo "[Info] Prompts : ${PROMPT_JSONL}"
echo "[Info] OutDir  : ${OUT_DIR}"

########################
# Run
########################
python vllm_infer.py \
  --model_path "${MODEL_PATH}" \
  --prompt_path "${PROMPT_JSONL}" \
  --raw_output_path "${RAW_OUT}" \
  --output_path "${FINAL_OUT}" \
  --gpu "${GPU}" \
  --batch_size "${BATCH_SIZE}" \
  --max_token_length "${MAX_LEN}" \
  --temperature "${TEMP}"

echo "[OK] Final output: ${FINAL_OUT}"
