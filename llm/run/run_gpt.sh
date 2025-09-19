eval_path='./data/mini_dev_sqlite.json' # _sqlite.json, _mysql.json, _postgresql.json
dev_path='./output/'
db_root_path='./data/dev_databases/'
use_knowledge='True'
mode='mini_dev' # dev, train, mini_dev
cot='True'

YOUR_API_KEY='YOUR_API_KEY'

# Choose the engine to run, e.g. gpt-4, gpt-4-32k, gpt-4-turbo, gpt-35-turbo, GPT35-turbo-instruct
engine='gpt-4-turbo'

# Choose the number of threads to run in parallel, 1 for single thread
num_threads=3

# Choose the SQL dialect to run, e.g. SQLite, MySQL, PostgreSQL
# PLEASE NOTE: You have to setup the database information in table_schema.py 
# if you want to run the evaluation script using MySQL or PostgreSQL
sql_dialect='SQLite'

# Choose the output path for the generated SQL queries
data_output_path='./exp_result/turbo_output/'
data_kg_output_path='./exp_result/turbo_output_kg/'

echo "generate $engine batch, run in $num_threads threads, with knowledge: $use_knowledge, with chain of thought: $cot"
python3 -u ./src/gpt_request.py --db_root_path ${db_root_path} --api_key ${YOUR_API_KEY} --mode ${mode} \
--engine ${engine} --eval_path ${eval_path} --data_output_path ${data_kg_output_path} --use_knowledge ${use_knowledge} \
--chain_of_thought ${cot} --num_process ${num_threads} --sql_dialect ${sql_dialect}