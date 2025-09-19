import re
from datetime import date, datetime
from db_utils import perform_query_on_sqlite_databases, execute_queries
import sqlite3
import json
from decimal import Decimal, ROUND_HALF_UP
import logging


def process_decimals(results, decimal_places):

    quantizer = Decimal(1).scaleb(-decimal_places)
    rounded = []
    for row in results:
        new_row = []
        for item in row:
            if isinstance(item, Decimal):
                new_row.append(item.quantize(quantizer, rounding=ROUND_HALF_UP))
            elif isinstance(item, float):
                new_row.append(round(item, decimal_places))
            else:
                new_row.append(item)
        rounded.append(tuple(new_row))
    return rounded


def remove_round_functions(sql_string):


    def find_matching_paren(text, start_pos):

        paren_count = 0
        for i in range(start_pos, len(text)):
            if text[i] == "(":
                paren_count += 1
            elif text[i] == ")":
                paren_count -= 1
                if paren_count == 0:
                    return i
        return -1

    def find_first_arg_end(text, start_pos):

        paren_count = 0
        for i in range(start_pos, len(text)):
            if text[i] == "(":
                paren_count += 1
            elif text[i] == ")":
                if paren_count == 0:
                    return i 
                paren_count -= 1
            elif text[i] == "," and paren_count == 0:
                return i  
        return len(text)

    result = sql_string

    while True:

        pattern = re.compile(r"ROUND\s*\(", re.IGNORECASE)
        match = pattern.search(result)

        if not match:
            break

        start_pos = match.start()
        open_paren_pos = match.end() - 1

        first_arg_end = find_first_arg_end(result, open_paren_pos + 1)

        close_paren_pos = find_matching_paren(result, open_paren_pos)

        if close_paren_pos == -1:
            break 


        first_arg = result[open_paren_pos + 1 : first_arg_end].strip()

        result = result[:start_pos] + first_arg + result[close_paren_pos + 1 :]

    return result


def remove_round_functions_regex(sql_string):
    pattern = r"ROUND\s*\(([^,()]*(?:\([^()]*\)[^,()]*)*?)(?:,[^)]*)?\)"
    while True:
        new_result = re.sub(pattern, r"\1", sql_string, flags=re.IGNORECASE)
        if new_result == sql_string: 
            break
        sql_string = new_result
    return sql_string


def remove_round(sql_list):

    cleaned = []
    for sql in sql_list:
        result = sql
        result = remove_round_functions(result)
        cleaned.append(result)
        if "ROUND" in result:
            logging.warning(f"ROUND found in {result}")
    return cleaned


def process_decimals_recursive(item, decimal_places):

    quantizer = Decimal(1).scaleb(-decimal_places)

    if isinstance(item, Decimal):
        return item.quantize(quantizer, rounding=ROUND_HALF_UP)
    elif isinstance(item, float):
        return round(item, decimal_places)
    elif isinstance(item, (list, tuple)):
        return type(item)(process_decimals_recursive(x, decimal_places) for x in item)
    elif isinstance(item, dict):
        return {
            k: process_decimals_recursive(v, decimal_places) for k, v in item.items()
        }
    else:
        return item


def preprocess_results(results, decimal_places=2):

    processed = []
    for result in results:
        processed_result = []
        for item in result:
            if isinstance(item, (date, datetime)):
                processed_result.append(item.strftime("%Y-%m-%d"))
            else:
                # 首先递归处理小数
                processed_item = process_decimals_recursive(item, decimal_places)
                if isinstance(processed_item, (dict, list)):
                    # 将不可哈希类型转换为其字符串表示形式，使用排序的键
                    processed_result.append(json.dumps(processed_item, sort_keys=True))
                else:
                    processed_result.append(processed_item)
        processed.append(tuple(processed_result))
    return processed


def remove_distinct(sql_list):


    cleaned_queries = []
    for query in sql_list:
        tokens = query.split(" ")
        filtered_tokens = []
        for token in tokens:
            if token.lower() != "distinct":
                filtered_tokens.append(token)
        cleaned_query = " ".join(filtered_tokens)
        cleaned_queries.append(cleaned_query)

    return cleaned_queries


def check_sql_function_usage(sqls, required_keywords):

    if not sqls:
        return 0

    combined_sql = " ".join(sql.lower() for sql in sqls)

    for kw in required_keywords:
        if kw.lower() not in combined_sql:
            return 0

    return 1


def ex_base(pred_sqls, sol_sqls, db_path, conn, conditions=None):

    if not pred_sqls or not sol_sqls:
        return 0

    predicted_res, pred_err, pred_to = execute_queries(
        pred_sqls, db_path, conn, None, ""
    )
    print(f"Predicted results: {predicted_res}")
    ground_res, gt_err, gt_to = execute_queries(sol_sqls, db_path, conn, None, "")
    print(f"Ground truth results: {ground_res}")
    if any([pred_err, pred_to, gt_err, gt_to]):
        return 0

    predicted_res = preprocess_results(predicted_res)
    ground_res = preprocess_results(ground_res)
    if not predicted_res or not ground_res:
        return 0

    if conditions is not None and conditions.get("order", False):
        return 1 if predicted_res == ground_res else 0
    else:
        return 1 if set(predicted_res) == set(ground_res) else 0


def performance_compare_by_qep(old_sqls, sol_sqls, db_path, conn):


    if not old_sqls or not sol_sqls:
        print("Either old_sqls or sol_sqls is empty. Returning 0.")
        return 0
    print(f"Old SQLs are {old_sqls}")
    print(f"New SQLs are {sol_sqls}")

    def measure_sqls_cost(sql_list):
        total_cost = 0.0
        for sql in sql_list:
            upper_sql = sql.strip().upper()
            if not (
                upper_sql.startswith("SELECT")
                or upper_sql.startswith("INSERT")
                or upper_sql.startswith("UPDATE")
                or upper_sql.startswith("DELETE")
            ):
                print(f"[measure_sqls_cost] Skip EXPLAIN for non-DML: {sql}")
                try:
                    perform_query_on_sqlite_databases(sql, db_path, conn=conn)
                except Exception as exc:
                    print(f"[measure_sqls_cost] Error executing non-DML '{sql}': {exc}")
                continue

            explain_sql = f"EXPLAIN QUERY PLAN {sql}"
            try:
                result_rows, _ = perform_query_on_sqlite_databases(
                    explain_sql, db_path, conn=conn
                )
                if not result_rows:
                    print(f"[measure_sqls_cost] No result returned for EXPLAIN: {sql}")
                    continue

                total_cost_part = 1.0 

                total_cost += float(total_cost_part)

            except sqlite3.Error as e:
                print(f"[measure_sqls_cost] SQLite Error on SQL '{sql}': {e}")
            except Exception as e:
                print(f"[measure_sqls_cost] Unexpected error on SQL '{sql}': {e}")

        return total_cost


    try:
        perform_query_on_sqlite_databases("BEGIN", db_path, conn=conn)
        old_total_cost = measure_sqls_cost(old_sqls)
        print(f"Old SQLs total plan cost: {old_total_cost}")
    finally:
        perform_query_on_sqlite_databases("ROLLBACK", db_path, conn=conn)

    try:
        perform_query_on_sqlite_databases("BEGIN", db_path, conn=conn)
        sol_total_cost = measure_sqls_cost(sol_sqls)
        print(f"Solution SQLs total plan cost: {sol_total_cost}")
    finally:
        perform_query_on_sqlite_databases("ROLLBACK", db_path, conn=conn)


    print(
        f"[performance_compare_by_qep] Compare old({old_total_cost}) vs. sol({sol_total_cost})"
    )
    return 1 if sol_total_cost < old_total_cost else 0


def remove_comments(sql_list):

    cleaned = []
    for sql in sql_list:
        no_block = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
        no_line = re.sub(r"--.*?(\r\n|\r|\n)", r"\1", no_block)
        no_blank = re.sub(r"\n\s*\n+", "\n", no_line)
        cleaned.append(no_blank.strip())
    return cleaned


def test_case_default(pred_sqls, sol_sqls, db_path, conn, conditions):

    pred_sqls = remove_comments(pred_sqls)
    sol_sqls = remove_comments(sol_sqls)
    pred_sqls = remove_distinct(pred_sqls)
    pred_sqls = remove_round(pred_sqls)
    sol_sqls = remove_distinct(sol_sqls)
    sol_sqls = remove_round(sol_sqls)

    result = ex_base(pred_sqls, sol_sqls, db_path, conn, conditions)
    assert result == 1, f"ex_base returned {result} but expected 1."
    return result


# 注意: 函数名应该是`test_case`，而不是`test_case_default`
TEST_CASE_DEFAULT = """
def test_case(pred_sqls, sol_sqls, db_path, conn, conditions):
   pred_sqls = remove_comments(pred_sqls)
   sol_sqls  = remove_comments(sol_sqls)
   pred_sqls = remove_distinct(pred_sqls)
   pred_sqls = remove_round(pred_sqls)
   sol_sqls  = remove_distinct(sol_sqls)
   sol_sqls  = remove_round(sol_sqls)
   result = ex_base(pred_sqls, sol_sqls, db_path, conn, conditions)
   assert result == 1, f"ex_base returned {result} but expected 1."
   return result
"""
