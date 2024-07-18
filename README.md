# Arcwise BIRD Agent

Arcwise team submission for https://bird-bench.github.io

## Usage

`dev_databases` / `train_databases` must be downloaded externally.

```bash
poetry install
poetry shell

# minidev generate db metadata
ANTHROPIC_API_KEY=sk-xxx \
python -m arcwise.generate_db_metadata.main \
  --db-path bird_evaluation/data/dev_databases \
  --tables-json bird_evaluation/data/dev_tables.json \
  --output-schemas-path bird_evaluation/data/schemas \
  --output-metadata-file bird_evaluation/data/dev_metadata.json


OPENAI_API_KEY=sk-xxxxx

# minidev evaluation (unaided)
python -m arcwise.agent.main \
  --db-path bird_evaluation/dev_databases \
  --metadata-file bird_evaluation/data/dev_metadata.json \
  --questions-file bird_evaluation/data/mini_dev_sqlite.json \
  --concurrency 5

# Custom model endpoint (OpenAI-compatible)
OPENAI_API_BASE=https://arcwisedata--bird-llama-inference-web.modal.run/v1
OPENAI_API_KEY=...

# augment with input/output schema hints
python -m arcwise.llama_predict \
  --metadata-file bird_evaluation/data/dev_metadata.json \
  --questions-file bird_evaluation/data/mini_dev_sqlite.json \
  --output-file questions_predictions.json \
  --model llama3-output-input \
  --output-file llama_predict.json \
  --concurrency 10
```
