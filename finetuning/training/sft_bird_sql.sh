#!/bin/bash
# set -x




nproc_per_node=4

# Set environment variables
export CUDA_VISIBLE_DEVICES=4,5,6,7
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
current_date="$(date +%Y_%m_%d)"
# Path configuration
MODEL_PATH="/path/to/Qwen2.5-3B-Instruct"
MODEL_NAME=$(basename "$MODEL_PATH")
TRAIN_DATA="/path/to/train_bird.parquet"
DEV_DATA="/path/to/dev_bird.parquet"
OUTPUT_DIR="/path/to/sft_checkpoints/${MODEL_NAME}/${current_date}"
LOG_DIR="/path/to/sft_logs/${MODEL_NAME}/${current_date}"
mkdir -p "$LOG_DIR"
mkdir -p "$OUTPUT_DIR"
# Generate log file name with current timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/training_${TIMESTAMP}.log"

echo "Starting training, log will be saved to: $LOG_FILE"


# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=== Starting BIRD SQL SFT training ==="
echo "GPU count: $nproc_per_node"
echo "Model path: $MODEL_PATH"
echo "Training data: $TRAIN_DATA"
echo "Output directory: $OUTPUT_DIR"

# Check if files exist
if [ ! -f "$TRAIN_DATA" ]; then
    echo "❌ Training data does not exist: $TRAIN_DATA"
    exit 1
fi

if [ ! -d "$MODEL_PATH" ]; then
    echo "❌ Model path does not exist: $MODEL_PATH"
    exit 1
fi
if [ ! -f "$DEV_DATA" ]; then
    echo "❌ Validation data does not exist: $DEV_DATA"
    exit 1
fi

{
  echo "GPU count: $nproc_per_node"
  echo "Model path: $MODEL_PATH"
  echo "Training data: $TRAIN_DATA"
  echo "Validation data: $DEV_DATA"
  echo "Output directory: $OUTPUT_DIR"
  echo "✅ All file checks passed, starting SFT training..."
  
  python -m torch.distributed.run \
    --standalone --nnodes=1 --nproc-per-node=$nproc_per_node \
    -m verl.trainer.fsdp_sft_trainer \
    data.train_files="$TRAIN_DATA" \
    data.val_files="$DEV_DATA" \
    data.prompt_key=prompt \
    data.response_key=response \
    data.micro_batch_size_per_gpu=1 \
    data.max_length=18000 \
    data.train_batch_size=128 \
    model.partial_pretrain="$MODEL_PATH" \
    model.enable_gradient_checkpointing=true \
    trainer.default_local_dir="$OUTPUT_DIR" \
    trainer.project_name=bird_sql_sft \
    trainer.experiment_name="$MODEL_NAME_bird_sql_sft" \
    trainer.total_epochs=2 \
    trainer.logger=['console','tensorboard'] \
    optim.lr=5e-5 \
    optim.weight_decay=0.01 \
    trainer.save_freq=55 \
    trainer.test_freq=25 \
    model.fsdp_config.model_dtype=bfloat16 \
    "$@"
  
  RET=$?
  if [ $RET -eq 0 ]; then
    echo "✅ SFT training completed, checkpoints saved to: $OUTPUT_DIR"
    echo "Latest checkpoints:"
    ls -1t "$OUTPUT_DIR" | head -5
    echo ""
    echo "SFT training successful! Now you can proceed with GRPO training."
  else
    echo "❌ SFT training failed"
  fi
} 2>&1 | tee -a "$LOG_FILE"


# if the model name is phi-4-mini-instruct, then run the following command
if [[ "$MODEL_NAME" == "Phi-4-mini-instruct" ]]; then
 # Find your original Phi4 model path
 ORIGINAL_PHI4_PATH="/path/to/Phi-4-mini-instruct"
 
 # Iterate through all checkpoint directories
 for checkpoint_dir in "$OUTPUT_DIR"/global_step_*; do
   if [ -d "$checkpoint_dir" ]; then
     echo "Processing checkpoint: $(basename "$checkpoint_dir")"
     # Copy necessary Python files
     cp "$ORIGINAL_PHI4_PATH/configuration_phi3.py" "$checkpoint_dir/" 2>/dev/null || echo "configuration_phi3.py not found"
     cp "$ORIGINAL_PHI4_PATH/modeling_phi3.py" "$checkpoint_dir/" 2>/dev/null || echo "modeling_phi3.py not found"
   fi
 done
fi