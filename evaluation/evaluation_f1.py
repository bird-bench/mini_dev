import sys
import argparse
import multiprocessing as mp
from func_timeout import func_timeout, FunctionTimedOut
from evaluation_utils import (
    load_jsonl,
    execute_sql,
    package_sqls,
    sort_results,
    print_data,
)


def calculate_row_match(predicted_row, ground_truth_row):
    """
    Calculate the matching percentage for a single row.

    Args:
    predicted_row (tuple): The predicted row values.
    ground_truth_row (tuple): The actual row values from ground truth.

    Returns:
    float: The match percentage (0 to 1 scale).
    """
    total_columns = len(ground_truth_row)
    matches = 0
    element_in_pred_only = 0
    element_in_truth_only = 0
    for pred_val in predicted_row:
        if pred_val in ground_truth_row:
            matches += 1
        else:
            element_in_pred_only += 1
    for truth_val in ground_truth_row:
        if truth_val not in predicted_row:
            element_in_truth_only += 1
    match_percentage = matches / total_columns
    pred_only_percentage = element_in_pred_only / total_columns
    truth_only_percentage = element_in_truth_only / total_columns
    return match_percentage, pred_only_percentage, truth_only_percentage


def calculate_f1_score(predicted, ground_truth):
    """
    Calculate the F1 score based on sets of predicted results and ground truth results,
    where each element (tuple) represents a row from the database with multiple columns.

    Args:
    predicted (set of tuples): Predicted results from SQL query.
    ground_truth (set of tuples): Actual results expected (ground truth).

    Returns:
    float: The calculated F1 score.
    """
    # if both predicted and ground_truth are empty, return 1.0 for f1_score
    if not predicted and not ground_truth:
        return 1.0

    # Drop duplicates
    predicted_set = set(predicted) if predicted else set()
    ground_truth_set = set(ground_truth)

    # convert back to list
    predicted = list(predicted_set)
    ground_truth = list(ground_truth_set)

    # Calculate matching scores for each possible pair
    match_scores = []
    pred_only_scores = []
    truth_only_scores = []
    for i, gt_row in enumerate(ground_truth):
        # rows only in the ground truth results
        if i >= len(predicted):
            match_scores.append(0)
            truth_only_scores.append(1)
            continue
        pred_row = predicted[i]
        match_score, pred_only_score, truth_only_score = calculate_row_match(
            pred_row, gt_row
        )
        match_scores.append(match_score)
        pred_only_scores.append(pred_only_score)
        truth_only_scores.append(truth_only_score)

    # rows only in the predicted results
    for i in range(len(predicted) - len(ground_truth)):
        match_scores.append(0)
        pred_only_scores.append(1)
        truth_only_scores.append(0)

    tp = sum(match_scores)
    fp = sum(pred_only_scores)
    fn = sum(truth_only_scores)

    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0

    f1_score = (
        2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
    )
    return f1_score


def result_callback(result):
    exec_result.append(result)


def execute_model(
    predicted_sql, ground_truth, db_place, idx, meta_time_out, sql_dialect
):
    try:
        res = func_timeout(
            meta_time_out,
            execute_sql,
            args=(
                predicted_sql,
                ground_truth,
                db_place,
                sql_dialect,
                calculate_f1_score,
            ),
        )
    except KeyboardInterrupt:
        sys.exit(0)
    except FunctionTimedOut:
        result = [(f"timeout",)]
        res = 0
    except Exception as e:
        result = [(f"error",)]  # possibly len(query) > 512 or not executable
        res = 0
    # print(result)
    # result = str(set([ret[0] for ret in result]))
    result = {"sql_idx": idx, "res": res}
    # print(result)
    return result


def run_sqls_parallel(
    sqls, db_places, num_cpus=1, meta_time_out=30.0, sql_dialect="SQLite"
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
                meta_time_out,
                sql_dialect,
            ),
            callback=result_callback,
        )
    pool.close()
    pool.join()


def compute_f1_by_diff(exec_results, diff_json_path):
    num_queries = len(exec_results)
    results = [res["res"] for res in exec_results]
    contents = load_jsonl(diff_json_path)
    simple_results, moderate_results, challenging_results = [], [], []

    for i, content in enumerate(contents):
        if content["difficulty"] == "simple":
            simple_results.append(exec_results[i])

        if content["difficulty"] == "moderate":
            moderate_results.append(exec_results[i])

        if content["difficulty"] == "challenging":
            try:
                challenging_results.append(exec_results[i])
            except:
                print(i)

    simple_f1 = sum([res["res"] for res in simple_results]) / len(simple_results) * 100
    moderate_f1 = (
        sum([res["res"] for res in moderate_results]) / len(moderate_results) * 100
    )
    challenging_f1 = (
        sum([res["res"] for res in challenging_results])
        / len(challenging_results)
        * 100
    )
    all_f1 = sum(results) / num_queries * 100
    count_lists = [
        len(simple_results),
        len(moderate_results),
        len(challenging_results),
        num_queries,
    ]
    return (
        simple_f1,
        moderate_f1,
        challenging_f1,
        all_f1,
        count_lists,
    )


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

    print("start calculate Soft F1")
    simple_acc, moderate_acc, challenging_acc, acc, count_lists = compute_f1_by_diff(
        exec_result, args.diff_json_path
    )
    score_lists = [simple_acc, moderate_acc, challenging_acc, acc]
    print_data(score_lists, count_lists,metric='Soft-F1',result_log_file=args.output_log_path)
    print(
        "==========================================================================================="
    )
    print(f"Finished EX evaluation for {args.sql_dialect} on Mini Dev set")
    print("\n\n")
