import json
import psycopg2
import pymysql
import sqlite3
import pandas as pd
import os
from datetime import datetime


def load_json(dir):
    with open(dir, "r") as j:
        contents = json.loads(j.read())
    return contents


def connect_postgresql():
    # Open database connection
    # Connect to the database
    db = psycopg2.connect(
        "dbname=BIRD user=postgres host=localhost password=1q2w3e4r5t!@ port=5432"
    )
    return db


def connect_mysql():
    # Open database connection
    # Connect to the database"
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",
        database="BIRD",
        unix_socket="/tmp/mysql.sock",
        # port=3306,
    )
    return db


def connect_db(sql_dialect, db_path):
    if sql_dialect == "SQLite":
        conn = sqlite3.connect(db_path)
    elif sql_dialect == "MySQL":
        conn = connect_mysql()
    elif sql_dialect == "PostgreSQL":
        conn = connect_postgresql()
    else:
        raise ValueError("Unsupported SQL dialect")
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

# FIXED!
def package_sqls(
    sql_path, db_root_path, engine, sql_dialect="SQLite", mode="gpt", data_mode="dev"
):
    clean_sqls = []
    db_path_list = []
    if mode == "gpt":
        sql_data = json.load(
            open(
                sql_path
                + "predict_"
                + data_mode
                + "_"
                + engine
                + "_"
                + sql_dialect.lower()
                + ".json",
                "r",
            )
        )
        for _, sql_str in sql_data.items():
            if type(sql_str) == str:
                sql, db_name = sql_str.split("\t----- bird -----\t")
            else:
                sql, db_name = " ", "financial"
            clean_sqls.append(sql)
            db_path_list.append(db_root_path + db_name + "/" + db_name + ".sqlite")

    elif mode == "gt":
        # fixed : sql_dialect lower()
        sqls = open(sql_path + data_mode + "_" + sql_dialect.lower() + "_gold.sql")
        sql_txt = sqls.readlines()
        # sql_txt = [sql.split('\t')[0] for sql in sql_txt]
        for idx, sql_str in enumerate(sql_txt):
            # print(sql_str)
            sql, db_name = sql_str.strip().split("\t")
            clean_sqls.append(sql)
            db_path_list.append(db_root_path + db_name + "/" + db_name + ".sqlite")

    return clean_sqls, db_path_list


def sort_results(list_of_dicts):
    return sorted(list_of_dicts, key=lambda x: x["sql_idx"])


def print_data(score_lists, count_lists, metric="F1 Score"):
    levels = ["simple", "moderate", "challenging", "total"]
    print("{:20} {:20} {:20} {:20} {:20}".format("", *levels))
    print("{:20} {:<20} {:<20} {:<20} {:<20}".format("count", *count_lists))

    print(
        f"======================================    {metric}    ====================================="
    )
    print("{:20} {:<20.2f} {:<20.2f} {:<20.2f} {:<20.2f}".format(metric, *score_lists))

def save_config_and_results(config, exec_result, score_lists, count_lists, test_dir, metric="EX"):
    # Create directory if it doesn't exist
    os.makedirs(test_dir, exist_ok=True)

    config_file = os.path.join(test_dir, "config.json")
    with open(config_file, 'w') as file:
        json.dump(config, file, indent=4)

    results_file = os.path.join(test_dir, "result.csv")
    if os.path.exists(results_file):
        df = pd.read_csv(results_file)
    else:
        df = pd.DataFrame(columns=["Metric", "Simple", "Moderate", "Challenging", "Total"])

    new_row = {
        "Metric": metric,
        "Simple": score_lists[0],
        "Moderate": score_lists[1],
        "Challenging": score_lists[2],
        "Total": score_lists[3]
    }

    # pd.concat을 사용하여 새로운 행을 DataFrame에 추가
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(results_file, index=False)

    detailed_results_file = os.path.join(test_dir, f"detailed_results_{metric}.csv")
    df_detailed = pd.DataFrame(exec_result)
    df_detailed.to_csv(detailed_results_file, index=False)

    return test_dir