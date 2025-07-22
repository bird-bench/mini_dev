#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed single instance evaluation script for SQLite
"""

import argparse
import json
import sys
import os
import io
import traceback
import time
import gc
from datetime import date

# Local imports
from logger import configure_logger, NullLogger
from utils import load_jsonl, split_field
from db_utils import (
    perform_query_on_sqlite_databases,
    close_sqlite_connection,
    execute_queries,
    get_connection_for_phase,
    reset_and_restore_database,
)
from test_utils import (
    check_sql_function_usage,
    remove_round,
    remove_distinct,
    remove_comments,
    preprocess_results,
    ex_base,
    TEST_CASE_DEFAULT,
    test_case_default,
)


def run_test_case(test_code, result, logger, conn, pred_sqls, sol_sqls, db_path, kwargs):
    """Execute a single test case"""
    global_env = {
        "perform_query_on_sqlite_databases": perform_query_on_sqlite_databases,
        "execute_queries": execute_queries,
        "ex_base": ex_base,
        "check_sql_function_usage": check_sql_function_usage,
        "remove_distinct": remove_distinct,
        "remove_comments": remove_comments,
        "remove_round": remove_round,
        "preprocess_results": preprocess_results,
        "pred_query_result": result,
        "date": date,
    }
    local_env = {
        "conn": conn,
        "pred_sqls": pred_sqls,
        "sol_sqls": sol_sqls,
        "db_path": db_path,
        "kwargs": kwargs,
    }

    logger.info(f"Executing test case")
    
    old_stdout = sys.stdout
    mystdout = io.StringIO()
    sys.stdout = mystdout

    try:
        test_case_code = "import datetime\nfrom datetime import date\n" + test_code
        test_case_code += "\n__test_case_result__ = test_case(pred_sqls, sol_sqls, db_path, conn, **kwargs)"
        
        exec(test_case_code, global_env, local_env)
        logger.info(f"Test case passed.")
        test_passed = True
        error_message = ""
        
    except AssertionError as e:
        logger.error(f"Test case failed due to assertion error: {e}")
        error_message = f"Test case failed due to assertion error: {e}\n"
        test_passed = False
        
    except Exception as e:
        logger.error(f"Test case failed due to error: {e}")
        error_message = f"Test case failed due to error: {e}\n"
        test_passed = False
        
    finally:
        sys.stdout = old_stdout

    captured_output = mystdout.getvalue()
    if captured_output.strip():
        logger.info(f"Captured output from test_code:\n{captured_output}")

    return test_passed, error_message


def execute_test_cases(test_cases, sql_result, logger, conn, pred_sqls, sol_sqls, db_path, kwargs):
    """Execute test cases sequentially"""
    passed_count = 0
    failed_tests = []
    test_error_messages = ""

    for i, test_case in enumerate(test_cases, start=1):
        logger.info(f"Starting test case {i}/{len(test_cases)}")

        try:
            test_passed, error_message = run_test_case(
                test_case, sql_result, logger, conn, pred_sqls, sol_sqls, db_path, kwargs
            )

            if test_passed:
                passed_count += 1
            else:
                failed_tests.append(f"test_{i}")
                test_error_messages += error_message

        except Exception as e:
            logger.error(f"Unexpected error executing test case {i}: {e}")
            failed_tests.append(f"test_{i}")
            test_error_messages += f"Unexpected error in test case {i}: {str(e)}\n"

    return passed_count, failed_tests, test_error_messages


def run_evaluation_phase(pred_sqls, sol_sqls, db_path, test_cases, logger, conn, efficiency, kwargs):
    """Execute evaluation phase"""
    error_message = ""
    sol_sql_result, exec_error_flag, timeout_flag, error_msg = execute_queries(
        pred_sqls, db_path, conn, logger, section_title="LLM Generated SQL", return_error=True
    )
    error_message += error_msg
    
    instance_execution_error = exec_error_flag
    instance_timeout_error = timeout_flag
    instance_assertion_error = False
    passed_count = 0
    failed_tests = []

    if not instance_execution_error and not instance_timeout_error and test_cases:
        passed_count, failed_tests, test_case_error_message = execute_test_cases(
            test_cases, sol_sql_result, logger, conn, pred_sqls, sol_sqls, db_path, kwargs
        )

        if failed_tests:
            instance_assertion_error = True
        if test_case_error_message:
            error_message += f"\nTest case errors: {test_case_error_message}\n"

    return (
        instance_execution_error,
        instance_timeout_error,
        instance_assertion_error,
        passed_count,
        failed_tests,
        error_message,
    )


def run_preprocessing(preprocess_sql, db_path, logger, conn):
    """Execute preprocessing SQL"""
    if preprocess_sql:
        execute_queries(preprocess_sql, db_path, conn, logger, section_title="Preprocess SQL")


def evaluate_instance(data, args, logger):
    """Evaluate a single instance and return results"""
    instance_id = data.get("instance_id", "unknown")
    
    # Check for required fields
    required_fields = ["selected_database", "preprocess_sql", "sol_sql"]
    if args.mode == "pred":
        required_fields.append("pred_sqls")

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        logger.error(f"Missing required fields: {', '.join(missing_fields)}")
        return {
            "instance_id": instance_id,
            "status": "failed",
            "error_message": f"Missing fields: {', '.join(missing_fields)}",
            "total_test_cases": len(data.get("test_cases", [])),
            "passed_test_cases": 0,
            "failed_test_cases": [],
            "evaluation_phase_execution_error": True,
            "evaluation_phase_timeout_error": False,
            "evaluation_phase_assertion_error": False,
        }

    # Extract data
    efficiency = data.get("efficiency", False)
    db_name = data["selected_database"]
    preprocess_sql = split_field(data, "preprocess_sql")
    clean_up_sql = split_field(data, "clean_up_sql")
    test_cases = data.get("test_cases", [])
    conditions = data.get("conditions", {})
    total_test_cases = len(test_cases)

    # Which solution field to use depends on --mode
    if args.mode == "gold":
        pred_sqls = split_field(data, "sol_sql")
    else:
        pred_sqls = split_field(data, "pred_sqls")
    
    sol_sqls = split_field(data, "sol_sql")
    
    # Set up kwargs
    kwargs = {}
    if not test_cases:
        test_cases = [TEST_CASE_DEFAULT]
        kwargs = {"conditions": conditions}

    # 🔧 CRITICAL FIX: Determine database path correctly
    ephemeral_db_path = os.environ.get("EPHEMERAL_DB_PATH")
    if ephemeral_db_path and os.path.exists(ephemeral_db_path):
        db_path = ephemeral_db_path
        logger.info(f"Using ephemeral database: {db_path}")
    else:
        db_path = f"./database/{db_name}/{db_name}.sqlite"
        logger.info(f"Using main database: {db_path}")
    
    # Get connection with retry
    db_connection = None
    max_retries = 3
    for attempt in range(max_retries):
        try:
            db_connection = get_connection_for_phase(db_path, logger)
            if db_connection:
                break
        except Exception as e:
            logger.error(f"Failed to get connection on attempt {attempt+1}: {e}")
            if attempt == max_retries - 1:
                return {
                    "instance_id": instance_id,
                    "status": "failed",
                    "error_message": f"Failed to get database connection after {max_retries} attempts",
                    "total_test_cases": total_test_cases,
                    "passed_test_cases": 0,
                    "failed_test_cases": [],
                    "evaluation_phase_execution_error": True,
                    "evaluation_phase_timeout_error": False,
                    "evaluation_phase_assertion_error": False,
                }
            time.sleep(1)  # Reduced wait time

    try:
        logger.info("=== Starting Evaluation Phase ===")

        # Run preprocessing SQL
        run_preprocessing(preprocess_sql, db_path, logger, db_connection)

        # Run evaluation phase tests
        (
            evaluation_phase_execution_error,
            evaluation_phase_timeout_error,
            evaluation_phase_assertion_error,
            passed_count,
            failed_tests,
            eval_error_message,
        ) = run_evaluation_phase(
            pred_sqls, sol_sqls, db_path, test_cases, logger, db_connection, efficiency, kwargs
        )

        # Cleanup SQL
        if clean_up_sql:
            logger.info("Executing Clean Up SQL")
            execute_queries(
                clean_up_sql, db_path, db_connection, logger, section_title="Clean Up SQL"
            )

        logger.info("=== Evaluation Phase Completed ===")

        # Determine status
        ret_status = "success"
        if (evaluation_phase_execution_error or 
            evaluation_phase_timeout_error or 
            evaluation_phase_assertion_error):
            ret_status = "failed"

        return {
            "instance_id": instance_id,
            "status": ret_status,
            "error_message": eval_error_message,
            "total_test_cases": total_test_cases,
            "passed_test_cases": passed_count,
            "failed_test_cases": failed_tests,
            "evaluation_phase_execution_error": evaluation_phase_execution_error,
            "evaluation_phase_timeout_error": evaluation_phase_timeout_error,
            "evaluation_phase_assertion_error": evaluation_phase_assertion_error,
        }

    except Exception as e:
        logger.error(f"Unexpected error evaluating instance: {e}")
        logger.error(traceback.format_exc())
        return {
            "instance_id": instance_id,
            "status": "failed",
            "error_message": f"Unexpected error: {str(e)}",
            "total_test_cases": total_test_cases,
            "passed_test_cases": 0,
            "failed_test_cases": [],
            "evaluation_phase_execution_error": True,
            "evaluation_phase_timeout_error": False,
            "evaluation_phase_assertion_error": False,
        }
    finally:
        if db_connection:
            try:
                close_sqlite_connection(db_path, db_connection)
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        # Reset database only if using ephemeral
        if ephemeral_db_path and os.path.exists(ephemeral_db_path):
            try:
                reset_and_restore_database(db_path, "123123", logger)
            except Exception as e:
                logger.error(f"Error during database reset: {e}")

        gc.collect()


def main():
    parser = argparse.ArgumentParser(description="Execute a single SQL solution and test case (SQLite).")
    parser.add_argument("--jsonl_file", help="Path to the JSONL file containing the dataset instance.", required=True)
    parser.add_argument("--output_file", required=True, help="Path to the JSON file for output with evaluation results.")
    parser.add_argument("--mode", help="gold or pred", choices=["gold", "pred"], default="pred")
    parser.add_argument("--logging", type=str, default="true", help="Enable or disable logging ('true' or 'false').")
    parser.add_argument("--log_file", type=str, help="Specific path for the log file.")

    args = parser.parse_args()

    try:
        # Load the data (expecting only one instance)
        data_list = load_jsonl(args.jsonl_file)
        if not data_list:
            print("No data found in the JSONL file.")
            sys.exit(1)

        data = data_list[0]  # Get the single instance
        instance_id = data.get("instance_id", 0)

        # Configure logger
        if args.logging == "true":
            if args.log_file:
                log_filename = args.log_file
            else:
                log_filename = os.path.splitext(args.jsonl_file)[0] + f"_instance_{instance_id}.log"
                print(f"Using log file: {log_filename}")
            logger = configure_logger(log_filename)
        else:
            logger = NullLogger()

        logger.info(f"Starting evaluation for instance {instance_id}")

        # Evaluate the instance
        evaluation_result = evaluate_instance(data, args, logger)

        # Write the output
        with open(args.output_file, "w") as f:
            json.dump(evaluation_result, f)

        logger.info(f"Evaluation completed for instance {instance_id}: {evaluation_result['status']}")
        sys.exit(0)
        
    except Exception as e:
        print(f"Error evaluating instance: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()