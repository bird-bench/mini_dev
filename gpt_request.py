#!/usr/bin/env python3
import json, os, time, argparse, openai, tqdm
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

from table_schema import generate_schema_prompt

def generate_comment_prompt(question, sql_dialect, knowledge=None):
    base_prompt = f"-- Using valid {sql_dialect}"
    knowledge_text = " and understanding External Knowledge" if knowledge else ""
    knowledge_prompt = f"-- External Knowledge: {knowledge}" if knowledge else ""
    combined_prompt = (f"{base_prompt}{knowledge_text}, answer the following questions for the tables provided above.\n-- {question}\n{knowledge_prompt}")
    return combined_prompt

def generate_cot_prompt(sql_dialect):
    return f"\nGenerate the {sql_dialect} for the above question after thinking step by step: "

def generate_instruction_prompt(sql_dialect):
    return f"""
        \nIn your response, you do not need to mention your intermediate steps. 
        Do not include any comments in your response.
        Do not need to start with the symbol ```
        You only need to return the result {sql_dialect} SQL code
        start from SELECT
        """

def generate_combined_prompts_one(db_path, question, sql_dialect, knowledge=None):
    schema_prompt = generate_schema_prompt(sql_dialect, db_path)
    comment_prompt = generate_comment_prompt(question, sql_dialect, knowledge)
    cot_prompt = generate_cot_prompt(sql_dialect)
    instruction_prompt = generate_instruction_prompt(sql_dialect)
    combined_prompts = "\n\n".join([schema_prompt, comment_prompt, cot_prompt, instruction_prompt])
    return combined_prompts

# openai configure
api_version = "2024-02-01"
api_base = "https://gcrendpoint.azurewebsites.net"
def new_directory(path):
    if not os.path.exists(path): os.makedirs(path)

# FIXME: Add a mo betta call using caching and whatnot. and LiteLLM
def connect_gpt(engine, prompt, max_tokens, temperature, stop, client):
    # Function to connect to the GPT API and get the response.
    MAX_API_RETRY = 10
    for _i in range(MAX_API_RETRY):
        time.sleep(2)
        try:
            if engine == "gpt-35-turbo-instruct":
                result = client.completions.create(model="gpt-3.5-turbo-instruct", prompt=prompt, max_tokens=max_tokens, temperature=temperature, stop=stop,)
                result = result.choices[0].text
            else:  # gpt-4-turbo, gpt-4, gpt-4-32k, gpt-35-turbo
                messages = [{"role": "user", "content": prompt},]
                result = client.chat.completions.create(model=engine, messages=messages, temperature=temperature, max_tokens=max_tokens, stop=stop,)
            break
        except Exception as e: #pylint: disable=broad-except
            result = "error:{}".format(e)
            print(result)
            time.sleep(4)
    return result

def decouple_question_schema(datasets, db_root_path):
    question_list = []
    db_path_list = []
    knowledge_list = []
    for _i, data in enumerate(datasets):
        question_list.append(data["question"])
        cur_db_path = db_root_path + data["db_id"] + "/" + data["db_id"] + ".sqlite"
        db_path_list.append(cur_db_path)
        knowledge_list.append(data["evidence"])
    return question_list, db_path_list, knowledge_list

def generate_sql_file(sql_lst, output_path=None):
    # Function to save the SQL results to a file.
    sql_lst.sort(key=lambda x: x[1])
    # result = {}
    # for i, (sql, _) in enumerate(sql_lst): result[i] = sql
    result = {i: sql for i, (sql, _) in enumerate(sql_lst)}
    if output_path:
        directory_path = os.path.dirname(output_path)
        new_directory(directory_path)
        json.dump(result, open(output_path, "w"), indent=4)
    return result

def init_client(api_key, api_version2, engine):
    # Initialize the AzureOpenAI client for a worker.
    # return AzureOpenAI(api_key=api_key, api_version=api_version2, base_url=f"{api_base}/openai/deployments/{engine}",)
    return openai.Client()

def post_process_response(response, db_path):
    sql = response if isinstance(response, str) else response.choices[0].message.content
    db_id = db_path.split("/")[-1].split(".sqlite")[0]
    sql = f"{sql}\t----- bird -----\t{db_id}"
    return sql

def worker_function(question_data):
    # Function to process each question, set up the client, generate the prompt, and collect the GPT response.
    prompt, engine, client, db_path, question, i = question_data
    response = connect_gpt(engine, prompt, 512, 0, ["--", "\n\n", ";", "#"], client)
    sql = post_process_response(response, db_path)
    print(f"Processed {i}th question: {question}")
    return sql, i

# (db_path_list, question_list, args.api_key, args.engine, args.sql_dialect, args.num_processes, klist)
def collect_response_from_gpt(db_path_list, question_list, api_key, engine, sql_dialect, num_threads=3, knowledge_list=None,):
    # Collect responses from GPT using multiple threads.
    client = init_client(api_key, api_version, engine)
    tasks = [(generate_combined_prompts_one(db_path=db_path_list[i], question=question_list[i], sql_dialect=sql_dialect, knowledge=knowledge_list[i],),
              engine, client, db_path_list[i], question_list[i], i)
             for i in range(len(question_list))]
    responses = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_task = {executor.submit(worker_function, task): task for task in tasks}
        for future in tqdm.tqdm(concurrent.futures.as_completed(future_to_task), total=len(tasks)):
            responses.append(future.result())
    return responses

# Choose the SQL dialect to run, e.g. SQLite, MySQL, PostgreSQL
# PLEASE NOTE: You have to setup the database information in table_schema.py
# if you want to run the evaluation script using MySQL or PostgreSQL
# Choose the output path for the generated SQL queries
# echo "generate $engine batch, run in $num_threads threads, with knowledge: $use_knowledge, with chain of thought: $cot"

def main():
    # ln -s ../minidev/MINIDEV data
    args = argparse.Namespace(
        eval_path = './data/mini_dev_sqlite.json', # _sqlite.json, _mysql.json, _postgresql.json
        mode = "mini_dev", # dev, train, mini_dev
        test_path = "",
        use_knowledge = "True",
        db_root_path = './data/dev_databases/',
        api_key = os.environ["OPENAI_API_KEY"], #FIXME: This isn't used for OpenAI.
        engine = 'gpt-4-turbo',
        data_output_path = './exp_result/turbo_output_kg/',
        chain_of_thought = "True",
        num_processes = 3,
        sql_dialect = "SQLite",
    )
    eval_data = json.load(open(args.eval_path, "r"))
    eval_data = eval_data[:9] # FIXME!!
    question_list, db_path_list, knowledge_list = decouple_question_schema(datasets=eval_data, db_root_path=args.db_root_path)
    assert len(question_list) == len(db_path_list) == len(knowledge_list)
    klist = knowledge_list if args.use_knowledge == "True" else None
    responses = collect_response_from_gpt(db_path_list, question_list, args.api_key, args.engine, args.sql_dialect, args.num_processes, klist)
    cot_str = '_cot' if args.chain_of_thought == "True" else ''
    output_name = f'{args.data_output_path}predict_{args.mode}_{args.engine}_{cot_str}_{args.sql_dialect}.json'
    generate_sql_file(sql_lst=responses, output_path=output_name)
    print(f"successfully collect results from {args.engine} for {args.mode} evaluation; SQL dialect {args.sql_dialect} Use knowledge: {args.use_knowledge}; Use COT: {args.chain_of_thought}")

if __name__ == "__main__": main()
