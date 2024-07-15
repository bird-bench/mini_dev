################################################################################################
################################################################################################
# <참고> 아래의 parameter를 입력하면 아래와 같이 실제로 연동되어 작동되니, 참고하여 작성
# diff_json_path => {ground_truth_path/{data_mode}_{sql_dialect.lower()}.json
# gold_sql_path => {ground_truth_path}/{data_mode}_{sql_dialect.lower()}_gold.sql
# predicted_json_path (predicted, in evaluation_utils.py) => {predicted_sql_path}/predicted_{data_mode}_{engine}_{sql_dialect.lower()}.json                  \
################################################################################################
################################################################################################

db_root_path='dummy/'
data_mode='mini_dev' # dev, train, mini_dev => 그냥 이름붙일 때 사용, 빼도 됨 
diff_json_path='./data/mini_dev_postgresql.json' # _sqlite.json, _mysql.json, _postgresql.json
# Path where the predicted SQL queries are stored
predicted_sql_path='./exp_result/sql_output_kg/'

ground_truth_path='./data/'
num_cpus=16
meta_time_out=30.0
mode_gt='gt'
mode_predict='gpt'

# Choose the engine to run, e.g. gpt-4, gpt-4-32k, gpt-4-turbo, gpt-35-turbo, GPT35-turbo-instruct
engine='gpt-4-turbo'


# Choose the SQL dialect to run, e.g. SQLite, MySQL, PostgreSQL
# PLEASE NOTE: You have to setup the database information in evaluation_utils.py 
# if you want to run the evaluation script using MySQL or PostgreSQL
sql_dialect='PostgreSQL'

timestamp=$(date +"%Y%m%d_%H%M%S")
test_dir="test_results/${engine}_${sql_dialect}_${timestamp}"
mkdir -p "${test_dir}"

echo "starting to compare with knowledge for ex engine: ${engine} sql_dialect: ${sql_dialect}"
python3 -u ./src/evaluation_ex.py --db_root_path ${db_root_path} --predicted_sql_path ${predicted_sql_path} --data_mode ${data_mode} \
--ground_truth_path ${ground_truth_path} --num_cpus ${num_cpus} --mode_gt ${mode_gt} --mode_predict ${mode_predict} \
--diff_json_path ${diff_json_path} --meta_time_out ${meta_time_out} --engine ${engine} --sql_dialect ${sql_dialect} --test_dir ${test_dir}

echo "starting to compare with knowledge for ves engine: ${engine} sql_dialect: ${sql_dialect}"
python3 -u ./src/evaluation_ves.py --db_root_path ${db_root_path} --predicted_sql_path ${predicted_sql_path} --data_mode ${data_mode} \
--ground_truth_path ${ground_truth_path} --num_cpus ${num_cpus} --mode_gt ${mode_gt} --mode_predict ${mode_predict} \
--diff_json_path ${diff_json_path} --meta_time_out ${meta_time_out} --engine ${engine} --sql_dialect ${sql_dialect} --test_dir ${test_dir}

echo "starting to compare with knowledge for soft-f1 engine: ${engine} sql_dialect: ${sql_dialect}"
python3 -u ./src/evaluation_f1.py --db_root_path ${db_root_path} --predicted_sql_path ${predicted_sql_path} --data_mode ${data_mode} \
--ground_truth_path ${ground_truth_path} --num_cpus ${num_cpus} --mode_gt ${mode_gt} --mode_predict ${mode_predict} \
--diff_json_path ${diff_json_path} --meta_time_out ${meta_time_out} --engine ${engine} --sql_dialect ${sql_dialect} --test_dir ${test_dir}