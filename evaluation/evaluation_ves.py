import sys
import json
import numpy as np
import argparse
import multiprocessing as mp
from func_timeout import func_timeout, FunctionTimedOut
from evaluation_utils import (
    load_jsonl,
    execute_sql,
    package_sqls,
    sort_results,
    print_data,
    connect_db,
)
import time
import math


def result_callback(result):
    exec_result.append(result)


def clean_abnormal(input):
    input = np.asarray(input)
    processed_list = []
    mean = np.mean(input, axis=0)
    std = np.std(input, axis=0)
    for x in input:
        if x < mean + 3 * std and x > mean - 3 * std:
            processed_list.append(x)
    return processed_list


def execute_sql(sql, db_path, sql_dialect, return_time=False):
    # Connect to the database
    conn = connect_db(sql_dialect, db_path)
    start_time = time.time()
    cursor = conn.cursor()
    cursor.execute(sql)
    res = cursor.fetchall()
    conn.close()  # Don't forget to close the connection!
    exec_time = time.time() - start_time
    if return_time:
        return exec_time

    return res


def iterated_execute_sql(
    predicted_sql, ground_truth, db_path, iterate_num, sql_dialect
):
    diff_list = []
    predicted_res = execute_sql(predicted_sql, db_path, sql_dialect)
    ground_truth_res = execute_sql(ground_truth, db_path, sql_dialect)
    reward = 0
    time_ratio = 0
    if set(predicted_res) == set(ground_truth_res):
        for _ in range(iterate_num):
            predicted_time = execute_sql(
                predicted_sql, db_path, sql_dialect, return_time=True
            )
            ground_truth_time = execute_sql(
                ground_truth, db_path, sql_dialect, return_time=True
            )
            diff_list.append(ground_truth_time / predicted_time)
        processed_diff_list = clean_abnormal(diff_list)
        time_ratio = sum(processed_diff_list) / len(processed_diff_list)
    if time_ratio == 0:
        reward = 0
    elif time_ratio >= 2:
        reward = 1.25
    elif time_ratio >= 1 and time_ratio < 2:
        reward = 1
    elif time_ratio >= 0.5 and time_ratio < 1:
        reward = 0.75
    elif time_ratio >= 0.25 and time_ratio < 0.5:
        reward = 0.5
    else:
        reward = 0.25
    # return time_ratio
    return reward


def execute_model(
    predicted_sql, ground_truth, db_place, idx, iterate_num, meta_time_out, sql_dialect
):
    try:
        # you can personalize the total timeout number
        # larger timeout leads to more stable ves
        # while it needs more your patience....
        reward = func_timeout(
            meta_time_out * iterate_num,
            iterated_execute_sql,
            args=(predicted_sql, ground_truth, db_place, iterate_num, sql_dialect),
        )
    except KeyboardInterrupt:
        sys.exit(0)
    except FunctionTimedOut:
        result = [(f"timeout",)]
        reward = 0
    except Exception as e:
        result = [(f"error",)]  # possibly len(query) > 512 or not executable
        reward = 0
    result = {"sql_idx": idx, "reward": reward}
    return result


def run_sqls_parallel(
    sqls,
    db_places,
    num_cpus=1,
    iterate_num=100,
    meta_time_out=30.0,
    sql_dialect="SQLite",
):
    pool = mp.Pool(processes=num_cpus)
    for i, sql_pair in enumerate(sqls):
        predicted_sql, ground_truth = sql_pair
        pool.apply_async(
            execute_model,
            args=(
                predicted_sql,
                ground_truth,
                db_places[i],
                i,
                iterate_num,
                meta_time_out,
                sql_dialect,
            ),
            callback=result_callback,
        )
    pool.close()
    pool.join()


def compute_ves(exec_results):
    num_queries = len(exec_results)
    total_reward = 0
    count = 0

    for i, result in enumerate(exec_results):
        if result["reward"] != 0:
            count += 1
        total_reward += math.sqrt(result["reward"]) * 100
    ves = total_reward / num_queries
    return ves


def compute_ves_by_diff(exec_results, diff_json_path):
    num_queries = len(exec_results)
    contents = load_jsonl(diff_json_path)
    simple_results, moderate_results, challenging_results = [], [], []
    for i, content in enumerate(contents):
        if content["difficulty"] == "simple":
            simple_results.append(exec_results[i])
        if content["difficulty"] == "moderate":
            moderate_results.append(exec_results[i])
        if content["difficulty"] == "challenging":
            challenging_results.append(exec_results[i])
    simple_ves = compute_ves(simple_results)
    moderate_ves = compute_ves(moderate_results)
    challenging_ves = compute_ves(challenging_results)
    all_ves = compute_ves(exec_results)
    count_lists = [
        len(simple_results),
        len(moderate_results),
        len(challenging_results),
        num_queries,
    ]
    return simple_ves, moderate_ves, challenging_ves, all_ves, count_lists


def print_reward_category(exec_results, engine, sql_dialect):
    res = {
        "engine": engine,
        "sql_dialect": sql_dialect,
        "distribution": exec_results,
    }
    file_path = "results.json"
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []  # Start with an empty list if file doesn't exist or is empty

    # Append the new data
    data.append(res)

    # Write the updated data back to the file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "--predicted_sql_path", type=str, required=True, default=""
    )
    args_parser.add_argument("--ground_truth_path", type=str, required=True, default="")
    args_parser.add_argument("--db_root_path", type=str, required=True, default="")
    args_parser.add_argument("--num_cpus", type=int, default=1)
    args_parser.add_argument("--meta_time_out", type=float, default=30.0)
    args_parser.add_argument("--diff_json_path", type=str, default="")
    args_parser.add_argument("--sql_dialect", type=str, default="SQLite")
    args_parser.add_argument("--output_log_path", type=str, default="SQLite")
    args = args_parser.parse_args()
    exec_result = []

    pred_queries, db_paths = package_sqls(
        args.predicted_sql_path,
        args.db_root_path,
        mode='pred'
    )
    # generate ground truth sqls:
    gt_queries, db_paths_gt = package_sqls(
        args.ground_truth_path,
        args.db_root_path,
        mode="gt",
    )
    query_pairs = list(zip(pred_queries, gt_queries))
    run_sqls_parallel(
        query_pairs,
        db_places=db_paths_gt,
        num_cpus=args.num_cpus,
        meta_time_out=args.meta_time_out,
        sql_dialect=args.sql_dialect,
    )
    exec_result = sort_results(exec_result)
    # print_reward_category(exec_result, args.engine, args.sql_dialect)
    print("start calculate R-VES")
    simple_ves, moderate_ves, challenging_ves, ves, count_lists = compute_ves_by_diff(
        exec_result, args.diff_json_path
    )
    score_lists = [simple_ves, moderate_ves, challenging_ves, ves]
    print_data(score_lists, count_lists, metric="R-VES",result_log_file=args.output_log_path)
    print(
        "==========================================================================================="
    )
    print(f"Finished R-VES evaluation for {args.sql_dialect} on Mini Dev set")
    print("\n\n")
