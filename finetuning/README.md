# BIRD-SQL Train — Code README

This README describes **how to prepare data, train, and run inference** for the [filtered BIRD-SQL Train set](https://huggingface.co/datasets/birdsql/BIRD-SQL-Train).


## 1 Data Processing

### 1.1 Pull dataset from Hugging Face
```python
from datasets import load_dataset
# Load the dataset
dataset = load_dataset("birdsql/bird23-train-filtered")
# Access the dataset
print(dataset["train"][0])
print("Saved to data/train.jsonl, size:", len(ds["train"]))
```
> New users: Please download BIRD train databases from [here](https://huggingface.co/datasets/birdsql/BIRD-SQL-Train/blob/main/birdsql_train_dbs.zip)


### 1.2 Split train/val by db_id

We use the Mini-Dev and original Dev sets as the test sets. For training purpose, we split the filtered train set into train/val sets by db_id (90%/10%) use the `./data_processing/split_data.py` and outputs: data/split_train.json, data/split_val.json

### 1.3 Data processing

We reuse the same two steps from the Arctic-Text2SQL-R1 project (see their [repo](https://github.com/snowflakedb/ArcticTraining/tree/main/projects/arctic_text2sql_r1) for details):
1. Build BM25 index for database values 
```bash
python3 data_preprocessing/build_contents_index.py \
--db-root /path/to/train_databases \
--index-root /path/to/db_contents_index \
--temp-dir /CREATE_TEMP_DIR \
--threads 16
```
2. Prepare the input and output sequences for both split train and val sets
```bash
bash data_preprocessing/process_dataset.sh \
 -i /path/to/split_train.json \
 -o /path/to/train_bird.json \
 -d /path/to/train_databases/ \
 -t /path/to/train_tables.json \
 -s bird \
 -m dev \
 -v 2 \
 -c /path/to/db_contents_index
```

```bash
bash data_preprocessing/process_dataset.sh \
 -i /path/to/split_val.json \
 -o /path/to/train_val.json \
 -d /path/to/train_databases/ \
 -t /path/to/train_tables.json \
 -s bird \
 -m dev \
 -v 2 \
 -c /path/to/db_contents_index
```

3. We will use the [verl](https://github.com/volcengine/verl/tree/main) training library for finetuning. Please install verl by following their official [instructions](https://verl.readthedocs.io/en/latest/start/install.html). verl requires the input data to be in the parquet format, so we convert the processed json files to parquet using the following script:
```bash
python ./data_processing/verl_data_process.py
```
Please setup the input/output paths in the script before running it. The output files will be saved as `train_bird.parquet` and `val_bird.parquet`.


## 2 Model Finetuning
We provide an example training script `finetuning/training/sft_bird_sql.sh` for finetuning the model on the BIRD-SQL Train set. Please modify the paths and parameters in the script before running it. The script uses a Qwen2.5-3B-Instruct model as an example, you can change it to other models as needed.


## 3 Inference & Evaluation

### 3.1 Inference with vLLM

We use [vLLM](https://github.com/vllm-project/vllm) for inference. Please refer to the official instructions for installation. We provide an example inference script `/inference/infer_bird_sql.sh`. We also provided the prompt file for both Mini-Dev and Dev dataset. Please modify the paths and parameters in the script before running it.

### 3.2 Evaluation

Please refer to the BIRD [Mini-Dev](https://github.com/bird-bench/mini_dev) repo for evaluation.