# text2sql-evaluation
- Forked from https://github.com/bird-bench/mini_dev
- main branch is using MySQL

## How to run

### 1. Set Database & Make Tables & Insert Data
- Setting MySQL by docker
```bash
docker pull mysql:8.0.36

docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=1q2w3e4r5t --name mysql-bird -v /mnt/mysql:/var/lib/mysql -v /:/mnt/host mysql:8.0.36 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

cd {path/to/dir}/MINIDEV_mysql/BIRD_dev.sql

docker exec -it mysql-bird /bin/bash

mysql -u root -p # 패스워드 입력 (1q2w3e4r5t)

# 이하 mysql console
CREATE DATABASE BIRD_MINI_DEV;

SHOW DATABASES;

USE BIRD_MINI_DEV;

source BIRD_dev.sql

SHOW TABLES; # Data Insert 확인
```
- Setting & Running DDL/DML Query
  - e.g. : mini-dev dataset
    1. download dataset : https://bird-bench.oss-cn-beijing.aliyuncs.com/minidev.zip
    2. run sql (minidev/minidev/MINIDEV_mysql/BIRD_dev.sql)

### 2. Set Parameters
- Modifying text2sql-evaluation/llm/run/run_evaluation.sh
  - predicted_sql_path : directory path for predicted json file
  - ground_truth_path : directory path for GT json and sql file
  - (CAUTION) file명 조합 방식이 약간 조잡한 부분이 있음. 맞춰주지 않을 경우 에러 발생하므로 주의
    - 추후 편의성 개선 고도화

### 3. Put Data file in the Right Place
- e.g. mini-dev dataset
  - Ground Truth
    - text2sql-evaluation/llm/data/mini_dev_mysql_gold.sql
    - text2sql-evaluation/llm/data/mini_dev_mysql.json
  - Prediction
    - text2sql-evaluation/llm/exp_result/sql_output_kg/predict_mini_dev_gpt-4_mysql.json

### 4. Set DB Connection
- Modifying connect_postgresql in text2sql-evaluation/llm/src/evaluation_utils.py
```python
def connect_postgresql():
    # Open database connection
    # Connect to the database
    db = psycopg2.connect(
        "dbname=BIRD user=postgres host=localhost password=1q2w3e4r5t!@ port=5432" # FIX THIS LINE
    )
    return db
```

### 5. Run run_evaluation.sh
```Shell
cd ./llm/
sh ./run/run_evaluation.sh
```

### 6. Check Test Result
- Test results are saved in test_results/
  - config.json
  - result.csv
  - detailed_results_EX.csv
  - detailed_results_VES.csv
  - detailed_results_F1.csv