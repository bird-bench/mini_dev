import sys, argparse, multiprocessing as mp, json, psycopg2, pymysql, sqlite3, os
from func_timeout import func_timeout, FunctionTimedOut

def connect_postgresql():
    return psycopg2.connect("dbname=bird user=postgres host=localhost password=li123911 port=5432")
def connect_mysql():
    return pymysql.connect(host="localhost", user="root", password="li123911", database="BIRD", unix_socket="/var/run/mysqld/mysqld.sock")

def connect_db(sql_dialect, db_path):
    if sql_dialect == "SQLite": conn = sqlite3.connect(db_path)
    elif sql_dialect == "MySQL": conn = connect_mysql()
    elif sql_dialect == "PostgreSQL": conn = connect_postgresql()
    else: raise ValueError("Unsupported SQL dialect")
    return conn

def execute_sql(predicted_sql, ground_truth, db_path, sql_dialect, calculate_func):
    conn = connect_db(sql_dialect, db_path)
    # Connect to the database
    cursor = conn.cursor()
    cursor.execute(predicted_sql)
    predicted_res = cursor.fetchall()
    cursor.execute(ground_truth)
    ground_truth_res = cursor.fetchall()
    conn.close()
    res = calculate_func(predicted_res, ground_truth_res)
    return res

def package_sqls(sql_path, db_root_path, mode="pred"):
    clean_sqls = []
    db_path_list = []
    if mode == "pred":
        # use chain of thought
        sql_data = json.load(open(sql_path, "r",))
        for _, sql_str in sql_data.items():
            if isinstance(sql_str, str):
                try:
                    sql, db_name = sql_str.split("\t----- bird -----\t")
                except ValueError:
                    sql = sql_str.strip()
                    db_name = "financial"
            else:
                sql = " "
                db_name = "financial"
            clean_sqls.append(sql)
    elif mode == "gt":
        sqls = open(sql_path)
        sql_txt = sqls.readlines()
        for idx, sql_str in enumerate(sql_txt):
            sql, db_name = sql_str.strip().split("\t")
            clean_sqls.append(sql)
            db_path_list.append(db_root_path + db_name + "/" + db_name + ".sqlite")
    return clean_sqls, db_path_list

def print_data(score_lists, count_lists, metric="F1 Score",result_log_file=None):
    levels = ["simple", "moderate", "challenging", "total"]
    print("{:20} {:20} {:20} {:20} {:20}".format("", *levels))
    print("{:20} {:<20} {:<20} {:<20} {:<20}".format("count", *count_lists))
    print(f"======================================    {metric}    =====================================")
    print("{:20} {:<20.2f} {:<20.2f} {:<20.2f} {:<20.2f}".format(metric, *score_lists))
    # Log to file in append mode
    # Marc: create the log file dir if it doesn't exist
    if not os.path.exists(result_log_file):
        os.makedirs(os.path.dirname(result_log_file), exist_ok=True)
    if result_log_file is not None:
        with open(result_log_file, "a") as log_file:
            log_file.write(f"start calculate {metric}\n")
            log_file.write("{:20} {:20} {:20} {:20} {:20}\n".format("", *levels))
            log_file.write("{:20} {:<20} {:<20} {:<20} {:<20}\n".format("count", *count_lists))
            log_file.write(f"======================================    {metric}   =====================================\n")
            log_file.write("{:20} {:<20.2f} {:<20.2f} {:<20.2f} {:<20.2f}\n".format(metric, *score_lists))
            log_file.write("===========================================================================================\n")
            log_file.write(f"Finished {metric} evaluation for mini dev set\n")
            log_file.write("\n")

# Marc: This is some weirdness right here...
exec_result = []
def result_callback(result):
    exec_result.append(result)

def calculate_ex(predicted_res, ground_truth_res):
    res = 0
    if set(predicted_res) == set(ground_truth_res): res = 1
    return res

def execute_model(predicted_sql, ground_truth, db_place, idx, meta_time_out, sql_dialect):
    try:
        res = func_timeout(meta_time_out, execute_sql, args=(predicted_sql, ground_truth, db_place, sql_dialect, calculate_ex),)
    except KeyboardInterrupt:
        sys.exit(0)
    except FunctionTimedOut:
        result = [(f"timeout",)]
        res = 0
    except Exception as e:
        result = [(f"error",)]  # possibly len(query) > 512 or not executable
        res = 0
    result = {"sql_idx": idx, "res": res}
    return result

def run_sqls_parallel(sqls, db_places, num_cpus=1, meta_time_out=30.0, sql_dialect="SQLite"):
    pool = mp.Pool(processes=num_cpus)
    for i, sql_pair in enumerate(sqls):
        predicted_sql, ground_truth = sql_pair
        pool.apply_async(execute_model, args=(predicted_sql, ground_truth, db_places[i], i, meta_time_out, sql_dialect,), callback=result_callback)
    pool.close()
    pool.join()

def compute_acc_by_diff(exec_results, diff_json_path):
    num_queries = len(exec_results)
    results = [res["res"] for res in exec_results]
    contents = json.load(open(diff_json_path, "r"))
    simple_results, moderate_results, challenging_results = [], [], []
    for res, content in zip(exec_results, contents):
        if content["difficulty"] == "simple":
            simple_results.append(res)
        if content["difficulty"] == "moderate":
            moderate_results.append(res)
        if content["difficulty"] == "challenging":
            challenging_results.append(res)
    simple_acc = sum([res["res"] for res in simple_results]) / len(simple_results)
    moderate_acc = sum([res["res"] for res in moderate_results]) / len(moderate_results)
    challenging_acc = sum([res["res"] for res in challenging_results]) / len(challenging_results)
    all_acc = sum(results) / num_queries
    count_lists = [len(simple_results), len(moderate_results), len(challenging_results), num_queries,]
    return (simple_acc * 100, moderate_acc * 100, challenging_acc * 100, all_acc * 100, count_lists,)

def main():
    base_name = 'predict_mini_dev_gpt-4-turbo__cot_SQLite'
    args = argparse.Namespace(
        predicted_sql_path = f'./exp_result/turbo_output_kg/{base_name}.json',
        ground_truth_path = './data/mini_dev_sqlite_gold.sql',
        db_root_path = './data/dev_databases/',
        num_cpus = 16,
        meta_time_out = 30.0,
        diff_json_path = './data/mini_dev_sqlite.json',
        sql_dialect = 'SQLite',
        output_log_path = f'./eval_result/{base_name}.txt',
    )
    pred_queries, db_paths = package_sqls(args.predicted_sql_path, args.db_root_path, mode='pred')
    # generate ground truth sqls:
    gt_queries, db_paths_gt = package_sqls(args.ground_truth_path, args.db_root_path, mode="gt",)
    query_pairs = list(zip(pred_queries, gt_queries))
    run_sqls_parallel(query_pairs, db_places=db_paths_gt, num_cpus=args.num_cpus, meta_time_out=args.meta_time_out, sql_dialect=args.sql_dialect,)
    exec_result.sort(key=lambda x: x["sql_idx"])
    # exec_result = sort_results(exec_result) # Marc: WTF is this??
    print("start calculate EX")
    simple_acc, moderate_acc, challenging_acc, acc, count_lists = compute_acc_by_diff(exec_result, args.diff_json_path)
    score_lists = [simple_acc, moderate_acc, challenging_acc, acc] 
    print_data(score_lists, count_lists, metric="EX", result_log_file=args.output_log_path)
    print("===========================================================================================")
    print(f"Finished EX evaluation for {args.sql_dialect} on Mini Dev set")
    print("\n\n")

if __name__ == "__main__": main()
