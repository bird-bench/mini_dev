from cmath import exp
import json
import litellm
import logging
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from evaluation_ex import connect_db
from query_db_schema import get_columns_schema

from sql_query_tool import query_database_with_llm

# Enable LiteLLM logging to show detailed information including thinking tokens
# litellm.set_verbose = True
# logging.basicConfig(level=logging.DEBUG)

SQL_DIALECT = "SQLite"

def post_process_response(response, db_id):
    sql = response if isinstance(response, str) else response.choices[0].message.content
    sql = f"{sql}\t----- bird -----\t{db_id}"
    return sql

def calculate_ex(predicted_res, ground_truth_res):
    res = 0
    if set(predicted_res) == set(ground_truth_res): res = 1
    return res

def calculate_ex_lenient(predicted_res, ground_truth_res):
    """
    Lenient comparison of SQL results with tolerance for numeric differences
    and unordered comparisons
    """
    def values_differ(val1, val2):
        """Check if two values differ, with lenient comparison rules"""
        if val1 == val2:
            return False
        elif isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            # Numeric comparison with tolerance
            return abs(float(val1) - float(val2)) >= 0.001
        elif (isinstance(val1, (list, tuple)) and isinstance(val2, (list, tuple))):
            # Array comparison - check if all elements in each array exist in the other
            list1, list2 = list(val1), list(val2)
            for item in list1:
                if not array_contains(list2, item):
                    return True
            for item in list2:
                if not array_contains(list1, item):
                    return True
            return False
        else:
            return True

    def array_contains(array, value):
        """Check if array contains value using lenient comparison"""
        for item in array:
            if not values_differ(item, value):
                return True
        return False
    
    # Convert to lists for easier handling
    predicted_list = list(predicted_res)
    ground_truth_list = list(ground_truth_res)
    
    # If exact equality, return 1
    if predicted_list == ground_truth_list:
        return 1
    
    # Check if results differ using lenient comparison
    if values_differ(predicted_list, ground_truth_list):
        return 0
    else:
        return 1
    
def execute_sql(predicted_sql, ground_truth, db_path, sql_dialect, calculate_func, cutoff=10, timeout=30):
    """Execute SQL with timeout to prevent hanging"""
    
    def run_sql():
        """Function to run SQL in a separate thread"""
        try:
            conn = connect_db(sql_dialect, db_path)
            cursor = conn.cursor()
            cursor.execute(predicted_sql)
            predicted_res = cursor.fetchall()
            cursor.execute(ground_truth)
            ground_truth_res = cursor.fetchall()
            conn.close()
            res = calculate_func(predicted_res, ground_truth_res)
            return res, predicted_res[:100], ground_truth_res[:100]
        except Exception as e:
            raise e
    
    # Create a queue to get the result from the thread
    result_queue = queue.Queue()
    exception_queue = queue.Queue()
    
    def thread_worker():
        try:
            result = run_sql()
            result_queue.put(result)
        except Exception as e:
            exception_queue.put(e)
    
    # Start the thread
    thread = threading.Thread(target=thread_worker)
    thread.daemon = True  # Dies when main thread dies
    thread.start()
    
    # Wait for the thread to complete with timeout
    thread.join(timeout)
    
    if thread.is_alive():
        # Thread is still running, timeout occurred
        raise TimeoutError(f"SQL execution timed out after {timeout} seconds")
    
    # Check if there was an exception
    if not exception_queue.empty():
        raise exception_queue.get()
    
    # Get the result
    if not result_queue.empty():
        return result_queue.get()
    else:
        raise RuntimeError("No result returned from SQL execution")

def extract_sql_from_response(response):
    # Extract the SQL query from the model's response
    if not isinstance(response, str):
        print("Response is not a string")
        print(response)
    sql_query = response
    
    # Remove markdown code blocks (```sqlite, ```sql, or just ```)
    if sql_query.startswith('```'):
        # Find the end of the opening code block marker
        first_newline = sql_query.find('\n')
        if first_newline != -1:
            sql_query = sql_query[first_newline + 1:]
        else:
            # If no newline, remove the entire ``` part
            sql_query = sql_query[3:]
    
    # Remove closing ``` if present
    if sql_query.endswith('```'):
        sql_query = sql_query[:-3]
    
    # Strip whitespace and newlines from beginning and end
    sql_query = sql_query.strip()
    
    return sql_query

def generate_sql(
    question,
    db_path,
    evidence,
    expansion_field="",
):
    db_name = db_path.split("/")[-2]

    response = query_database_with_llm(
        db_name,
        question,
        evidence
        )

    sql_query = extract_sql_from_response(response)
    
    return sql_query

expansion_type = ""

expanded_item_ids = {item["question_id"]: item[expansion_type] for item in json.load(open("question_evidence_revised_analysis.json", "r")) if item.get(expansion_type, "") != ""}

print(f"Total expanded item ids {len(expanded_item_ids)}")

USE_CACHED = False
cache_file = "cached/gemini-25-pro_basic_prompt_new.json"

def process_single_item(item):
    """Process a single item - useful for threading"""
    question = item["question"]
    db_id = item["db_id"]
    db_path = "./data/dev_databases/{}/{}.sqlite".format(db_id, db_id)
    question_id = item["question_id"]
    evidence = item["evidence"]
    difficulty = item["difficulty"]
    ground_truth_sql = item.get("SQL", item.get("ground_truth_sql"))
    # use_expanded = question_id in expanded_item_ids
    expansion_field = expanded_item_ids.get(item["question_id"], "") if expansion_type else ""

    if USE_CACHED:
        if expansion_field == "":
            with open(cache_file, "r") as f:
                cached_data = json.load(f)
            for item in cached_data:
                if item["question_id"] == question_id:
                    # print(f"# Returning cached SQL for question_id {question_id}")
                    return item
    try:
        print("generating sql for question_id:", question_id)
        sql_query = generate_sql(question, db_path, evidence, expansion_field, sql_dialect=SQL_DIALECT)

        result = {
            "question_id": question_id,
            "db_id": db_id,
            "question": question,
            "evidence": evidence,
            "difficulty": difficulty,
            "predicted_sql": sql_query,
            "ground_truth_sql": ground_truth_sql,
        }
        return result
    except Exception as e:
        print(f"Error processing question {question_id}: {e}")
        return {
            "question_id": question_id,
            "db_id": db_id,
            "question": question,
            "evidence": evidence,
            "difficulty": difficulty,
            "predicted_sql": f"ERROR: {str(e)}",
            "ground_truth_sql": ground_truth_sql,
        }

if __name__ == "__main__":
    INPUT_JSON = "data/mini_dev_sqlite.json"
    OUTPUT_JSON = "tool_results_errors.json"
    PREVIOUS_FAILURES_FILE = "tool_results_evaluation_failures.json"
    failures = [item['question_id'] for item in json.load(open(PREVIOUS_FAILURES_FILE, "r"))]
    

    with open(INPUT_JSON, "r") as f:
        data = json.load(f)

    # data = [x for x in data if x["db_id"] == 'formula_1']
    # data = [item for item in data if item.get("question_id", "") in [563, 595]]
    # data = [x for x in data if x["exact_match"] == 1]
    # data = [x for x in data if x["question_id"] in failures]
    data = data[:]
    results = []

    # Use ThreadPoolExecutor for concurrent processing
    max_workers = 10 # Adjust based on your API rate limits and system
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_item = {executor.submit(process_single_item, item): item for item in data}
        
        # Process completed futures with progress bar
        with tqdm(total=len(data), desc="Processing questions") as pbar:
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                    pbar.set_postfix(db_id=result["db_id"])
                except Exception as e:
                    print(f"Error processing item {item.get('question_id', 'unknown')}: {e}")
                pbar.update(1)

    # Save results to JSON file
    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {OUTPUT_JSON}")



    # EVALUATE
    EVALUATION_OUTPUT_JSON = OUTPUT_JSON.replace(".json", "_evaluation.json")
    evaluation_results = []

    with open(OUTPUT_JSON, "r") as f:
        results = json.load(f)

    total_questions = len(results)
    correct_count = 0
    
    for i, result in enumerate(results):
        predicted_sql = result["predicted_sql"]
        ground_truth_sql = result["ground_truth_sql"]
        question = result["question"]
        evidence = result["evidence"]
        difficulty = result["difficulty"]
        db_id = result["db_id"]
        db_path = "./data/dev_databases/{}/{}.sqlite".format(db_id, db_id)
        question_id = result["question_id"]

        # Calculate exact match
        try:
            em, predicted_result, ground_truth_result = execute_sql(predicted_sql, ground_truth_sql, db_path, SQL_DIALECT, calculate_ex_lenient, timeout=30)
        except TimeoutError:
            print(f"Timeout evaluating question {result['question_id']}: SQL execution took too long")
            em, predicted_result, ground_truth_result = 0, [], []
        except Exception as e:
            print(f"Error evaluating question {result['question_id']}: {e}")
            em, predicted_result, ground_truth_result = 0, [], []

        if em == 1:
            correct_count += 1

        eval_result = {
            "question_id": result["question_id"],
            "db_id": db_id,
            "question": question,
            "evidence": evidence,
            "difficulty": difficulty,
            "predicted_sql": predicted_sql,
            "ground_truth_sql": ground_truth_sql,
            "predicted_result": predicted_result,
            "ground_truth_result": ground_truth_result,
            "exact_match": em
        }
        evaluation_results.append(eval_result)
        
        # Print progress at every 10% milestone
        progress_percentage = (i + 1) / total_questions * 100
        if (i + 1) % max(1, total_questions // 10) == 0 or i == total_questions - 1:
            current_accuracy = correct_count / (i + 1) * 100
            print(f"Progress: {i + 1}/{total_questions} ({progress_percentage:.1f}%) - Correct: {correct_count} - Accuracy: {current_accuracy:.1f}%")

    # Save evaluation results to JSON file
    with open(EVALUATION_OUTPUT_JSON, "w") as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"Evaluation results saved to {EVALUATION_OUTPUT_JSON}")
    
    # Make post-processed json file in bird format
    POSTPROCESSED_OUTPUT_JSON = EVALUATION_OUTPUT_JSON.replace(".json", "_postprocessed.json")

    postprocessed_results = {}
    question_to_index_dict = json.load(open("question_sql_idx_mapping.json", "r"))
    for result in evaluation_results:
        # get index from question_to_index_dict
        question = result["question"]
        sql_idx = question_to_index_dict[question]
        predicted_sql = result["predicted_sql"]
        processed_sql = post_process_response(predicted_sql, result["db_id"])
        postprocessed_results[str(sql_idx)] = processed_sql
        # order by sql_idx
    postprocessed_results = dict(sorted(postprocessed_results.items(), key=lambda item: int(item[0])))
    
    with open(POSTPROCESSED_OUTPUT_JSON, "w") as f:
        json.dump(postprocessed_results, f, indent=4)
    
    print(f"Post-processed results saved to {POSTPROCESSED_OUTPUT_JSON}")

    # Save failures to separate JSON file
    FAILURES_OUTPUT_JSON = EVALUATION_OUTPUT_JSON.replace(".json", "_failures.json")
    failures = [result for result in evaluation_results if result["exact_match"] == 0]
    with open(FAILURES_OUTPUT_JSON, "w") as f:
        json.dump(failures, f, indent=2)
    
    print(f"Failures saved to {FAILURES_OUTPUT_JSON}")
    
    # Print summary statistics
    total_questions = len(evaluation_results)
    correct_answers = sum(1 for result in evaluation_results if result["exact_match"] == 1)
    accuracy = correct_answers / total_questions if total_questions > 0 else 0
    
    print(f"Summary: {correct_answers}/{total_questions} correct ({accuracy:.2%} accuracy)")
    
    # Statistics by database
    db_stats = {}
    for result in evaluation_results:
        db_id = result["db_id"]
        if db_id not in db_stats:
            db_stats[db_id] = {"total": 0, "correct": 0}
        db_stats[db_id]["total"] += 1
        if result["exact_match"] == 1:
            db_stats[db_id]["correct"] += 1
    
    print("\n--- Statistics by Database ---")
    for db_id, stats in sorted(db_stats.items()):
        db_accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        print(f"{db_id}: {stats['correct']}/{stats['total']} correct ({db_accuracy:.2%} accuracy)")
    
    # Save database statistics to JSON file
    DB_STATS_JSON = "database_statistics.json"
    db_stats_with_accuracy = {}
    for db_id, stats in db_stats.items():
        db_accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        db_stats_with_accuracy[db_id] = {
            "total": stats["total"],
            "correct": stats["correct"],
            "accuracy": db_accuracy
        }
    
    with open(DB_STATS_JSON, "w") as f:
        json.dump(db_stats_with_accuracy, f, indent=2)
    
    print(f"\nDatabase statistics saved to {DB_STATS_JSON}")
