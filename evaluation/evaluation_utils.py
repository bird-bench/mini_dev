import json
import psycopg2
import pymysql
import sqlite3

def load_jsonl(file_path):
    data = []
    with open(file_path, "r") as file:
        for line in file:
            data.append(json.loads(line))
    return data

def load_json(dir):
    with open(dir, "r") as j:
        contents = json.loads(j.read())
    return contents


# psycopg2   2.9.9
def connect_postgresql():
    # Open database connection
    # Connect to the database
    db = psycopg2.connect(
        "dbname=bird user=postgres host=localhost password=li123911 port=5432"
    )
    return db


# PyMySQL  1.1.1
def connect_mysql():
    # Open database connection
    # Connect to the database"
    db = pymysql.connect(
        host="localhost",
        user="root",
        password="li123911",
        database="BIRD",
        # unix_socket="/tmp/mysql.sock",
        unix_socket="/var/run/mysqld/mysqld.sock"
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


def package_sqls(
    sql_path, db_root_path, mode="pred"
):
    clean_sqls = []
    db_path_list = []
    if mode == "pred":
        # use chain of thought
        sql_data = json.load(
            open(
                sql_path,
                "r",
            )
        )
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


def sort_results(list_of_dicts):
    return sorted(list_of_dicts, key=lambda x: x["sql_idx"])


def print_data(score_lists, count_lists, metric="F1 Score",result_log_file=None):
    levels = ["simple", "moderate", "challenging", "total"]
    print("{:20} {:20} {:20} {:20} {:20}".format("", *levels))
    print("{:20} {:<20} {:<20} {:<20} {:<20}".format("count", *count_lists))

    print(
        f"======================================    {metric}    ====================================="
    )
    print("{:20} {:<20.2f} {:<20.2f} {:<20.2f} {:<20.2f}".format(metric, *score_lists))
    
     # Log to file in append mode
    if result_log_file is not None:
        with open(result_log_file, "a") as log_file:
            log_file.write(f"start calculate {metric}\n")
            log_file.write("{:20} {:20} {:20} {:20} {:20}\n".format("", *levels))
            log_file.write(
                "{:20} {:<20} {:<20} {:<20} {:<20}\n".format("count", *count_lists)
            )
            log_file.write(
                f"======================================    {metric}   =====================================\n"
            )
            log_file.write(
                "{:20} {:<20.2f} {:<20.2f} {:<20.2f} {:<20.2f}\n".format(
                    metric, *score_lists
                )
            )
            log_file.write(
                "===========================================================================================\n"
            )
            log_file.write(f"Finished {metric} evaluation for mini dev set\n")
            log_file.write("\n")
