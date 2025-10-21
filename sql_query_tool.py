"""
SQL Query Tool for Function-Calling LLMs

This module provides a tool definition and implementation for executing SQL SELECT queries
on databases. It's designed to be used with OpenAI's function calling feature.
"""

import sqlite3
import json
from typing import Any, Dict
import litellm
from query_db_schema import get_columns_schema


# OpenAI Tool Schema Definition
SQL_QUERY_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "execute_sql_query",
        "description": "Execute a SELECT SQL query on a SQLite database and return the results. Use this tool to run read-only queries on the database.",
        "parameters": {
            "type": "object",
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "The SQL SELECT query to execute."
                }
            },
            "required": ["sql_query"]
        }
    }
}


def execute_sql_query(db_name: str, sql_query: str) -> Dict[str, Any]:
    """
    Execute a SQL SELECT query on a SQLite database.
    
    Args:
        db_name (str): Name of the SQLite database
        sql_query (str): SQL SELECT query to execute
        
    Returns:
        Dict[str, Any]: Dictionary containing query results, column names, and metadata
        
    Raises:
        ValueError: If the query is not a SELECT statement
        sqlite3.Error: If there's a database error
        FileNotFoundError: If the database file doesn't exist
    """
    
    # Security check: only allow SELECT queries
    query_stripped = sql_query.strip().upper()
    if not query_stripped.startswith('SELECT'):
        return {
            "success": False,
            "error": "Only SELECT queries are allowed for security reasons",
            "error_type": "security_error"
        }
    
    db_path = f"data/dev_databases/{db_name}/{db_name}.sqlite"
    try:
        # Connect to the database
        with sqlite3.connect(db_path) as conn:
            # Enable row factory to get column names
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Execute the query
            cursor.execute(sql_query)
            
            # Fetch all results
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            results = []
            column_names = []
            
            if rows:
                # Get column names from the first row
                column_names = list(rows[0].keys())
                
                # Convert each row to a dictionary
                for row in rows:
                    results.append((list(row)))
            
            return {
                "success": True,
                "data": results,
                "column_names": column_names,
                "row_count": len(results),
                "query": sql_query
            }
            
    except sqlite3.Error as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
            "error_type": "database_error",
            "query": sql_query
        }
    
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Database file not found: {db_path}",
            "error_type": "file_not_found",
            "query": sql_query
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown_error",
            "query": sql_query
        }
    


def format_query_results(results: Dict[str, Any], max_rows: int = 5) -> str:
    """
    Format query results for display in a human-readable way.
    
    Args:
        results (Dict[str, Any]): Results from execute_sql_query
        max_rows (int): Maximum number of rows to display
        
    Returns:
        str: Formatted string representation of the results
    """
    if not results["success"]:
        return f"Error: {results['error']}"
    
    if not results["data"]:
        return "Query executed successfully but returned no results."
    
    # Show data rows (limited by max_rows) as dictionaries
    rows = results["data"]
    column_names = results["column_names"]
    displayed_rows = rows[:min(len(rows), max_rows)]
    
    output = []
    total_rows = len(results["data"])
    displayed_count = len(displayed_rows)
    
    if total_rows > max_rows:
        output.append(f"Displaying first {displayed_count} rows of {total_rows}")
        output.append("")
    
    for i, row in enumerate(displayed_rows):
        # Create dictionary for this row
        row_dict = {}
        for j, value in enumerate(row):
            column_name = column_names[j] if j < len(column_names) else f"col_{j}"
            row_dict[column_name] = value
        
        output.append(f"Row {i}: {row_dict}")
        if i < len(displayed_rows) - 1:  # Add blank line between rows except after last row
            output.append("")


    
    if total_rows > max_rows:
        output.append("")
        output.append(f"... and {total_rows - max_rows} more rows")

    extra_instructions  = "Here is the output of the executed SQL query.\n\n"
    return extra_instructions+"\n".join(output)


def execute_sql_query_and_return_pretty_results(db_name: str, sql_query: str) -> str:
    print(f"Executing SQL Query:\n{sql_query}\n")
    results = execute_sql_query(db_name, sql_query)
    return format_query_results(results)



def get_schema_prompt(db_name: str, question: str, evidence: str) -> str:    # look up column suggestions

    with open("add_suggested_columns_results.json", "r") as f:
        suggested_columns_data = json.load(f)
    # find entry for this question
    suggested_columns = []
    for item in suggested_columns_data:
        if item["question"] == question and item["evidence"] == evidence:
            suggested_columns = item.get("expanded_column_suggestions", [])
            if not suggested_columns:
                print(f"No suggested columns found for question {item['question']}")
            break
    if not suggested_columns:
        print(f"No suggested columns found for question: {question} with evidence: {evidence}")

    schema_prompt = get_columns_schema(db_name, suggested_columns, schema_file="database_columns_schema.json")

    return schema_prompt

def query_database_with_llm(db_name: str, natural_language_query: str, evidence: str, model: str = "gemini/gemini-2.5-pro") -> str:
    """
    Use an LLM with function calling to answer natural language queries about a database.
    
    Args:
        db_name (str): Name of the SQLite database
        natural_language_query (str): Natural language question about the database
        evidence (str): Evidence field from the dataset
        model (str): LiteLLM model identifier for the LLM to use
        
    Returns:
        str: The LLM's response after potentially querying the database
    """


    # Available tools for the LLM
    tools = [SQL_QUERY_TOOL_SCHEMA]
    
    # System message to guide the LLM
    system_message = """You are an expert SQL programmer. Your job is to help the user construct SQL queries to answer questions about a database.

The user will give you a database schema, along with a natural language question about the database, and some guidance for formulating a SQL query. Your job is to return a SQLite query that can be executed to answer the question. Always take into account the guidance provided by the user.

You can also use the execute_sql_query tool to check the execution of your proposed query before responding. If you are unsure about which tables and columns to use, you can also use the tool to run test queries on the database.

Your final response to the user must always be a successful SQL query. Never return a message with empty content.
"""

    schema_prompt = get_schema_prompt(db_name, natural_language_query, evidence)

    PROMPT = """Using the tables above, generate a {sql_dialect} query to answer the question below. You are also given important guidance about how to construct your query correctly. Make sure to follow the guidance.

    QUESTION:
    {question}
    GUIDANCE:
    {evidence}

    Now, think carefully step by step. First think about which tables and columns to use. Use the execute_sql_query tool to examine the first few rows of the relevant tables, with the columns you are interested in by running queries like:

    SELECT column_name_1, column_name_2 FROM table_name LIMIT 5;
    
    Then generate a {sql_dialect} query for the above question, following the guidance provided above. Adhere to the following rules:

    - In your response, you do not need to mention your intermediate steps. 
    - Do not include any comments in your response.
    - NEVER start with the symbol ```
    - Your response should begin with SELECT or WITH.
    - You must always return {sql_dialect} SQL code.
    - Write syntactically correct, efficient SQL code that can be executed on the database.

    Extra things to remember:
        - Use COUNT(DISTINCT ...) when counting unique values.
        - If asked to calculate a ratio or percentage, always make sure the numerator and denominator are the right way around, based on the question and guidance. If the question or guidance asks for a percentage, remember to multiply by 100.0.
        - If the question asks for a first name and last name, return them as separate columns, not concatenated.
        - Your query should only return the columns requested in the question and guidance. Don't include extra columns, even if these were used in joins.
        - When counting, matching, or grouping individuals, you should retrieve on unique identifier columns, if these exist and it seems reasonable to do so.
        - Your query must never compare a datetime column directly with a date string. Extract the date part using a date function first.
        - Double-check that your query contains the same >=, >, <=, < operators as the question and guidance, if any.
        - Always make sure that the table and column names in your query are consistent with the schema provided.
        - If there is more than one column or table with a similar name, choose the one that most closely matches the word used in the question.
        - Very important: always make sure that your query takes into account the guidance provided. If the question or guidance mentions specific columns or filter logic, ensure these are reflected in your query.
        
    Here are the question and guidance again for your reference:

    QUESTION:
    {question}
    GUIDANCE:
    {evidence}

    Always use the execute_sql_query tool to verify your SQL query before returning it. If the query's output looks reasonable, you should return the SQL query itself as your final response. Remember that the query should return only the columns requested in the question and guidance.
    If the output does not look reasonable given the question, revise your SQL query and try again. A SQL query that returns no results is unlikely to be correct -- revise and try again.
    Your final response to the user must always be a successful SQL query.
"""

    PROMPT = "DATABASE SCHEMA:\n" + schema_prompt + "\n\n------ END OF SCHEMA ------\n\n" + PROMPT.format(
        sql_dialect="SQLite",
        question=natural_language_query,
        evidence=evidence
    )

    # print(PROMPT)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": PROMPT}
    ]

    try:
        # Make the initial LLM call
        response = litellm.completion(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            thinking={"type": "enabled", "budget_tokens": 512},
            temperature=0.0,
            max_retries=5,
        )
        
        # Handle the response and any tool calls
        while response.choices[0].message.tool_calls:
            print("Processing tool calls...")
            print(response.choices[0].message.tool_calls)
            # Add the assistant's message (with tool calls) to the conversation
            messages.append(response.choices[0].message)
            
            # Process each tool call
            for tool_call in response.choices[0].message.tool_calls:
                if tool_call.function.name == "execute_sql_query":
                    # Parse the function arguments
                    args = json.loads(tool_call.function.arguments)
                    
                    # Execute the SQL query
                    result = execute_sql_query_and_return_pretty_results(db_name, args["sql_query"])
                    
                    # Add the tool result to the conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
            
            # Get the next response from the LLM
            response = litellm.completion(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                thinking={"enabled": True, "budget_tokens": 512},
                temperature=0.0,
                max_retries=5,
            )
        print("HERE")
        response_content = response.choices[0].message.content
        messages.append(response.choices[0].message)

        retry_count = 0
        max_retries = 8
        while response_content is None and retry_count < max_retries:
            retry_count += 1
            print(f"LLM returned an empty response, retrying... (attempt {retry_count}/{max_retries})")
            messages.append({
                "role": "system",
                "content": "Please continue and ensure that your final response is a valid SQL query starting with SELECT or WITH."
            })
            response = litellm.completion(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                thinking={"enabled": True, "budget_tokens": 512},
                temperature=0.0,
                max_retries=5,
            )
            messages.append(response.choices[0].message)
            response_content = response.choices[0].message.content

        if response_content is None:
            print(f"Failed to get valid response after {max_retries} attempts")

        print("FINAL CONVERSATION:\n")
        # Convert messages to serializable format
        serializable_messages = []
        for msg in messages[2:]:
            if hasattr(msg, 'model_dump'):
                # LiteLLM message object
                msg_dict = msg.model_dump()
            elif hasattr(msg, 'dict'):
                # Pydantic model
                msg_dict = msg.dict()
            else:
                # Regular dict
                msg_dict = msg
            
            # Remove signature field from thinking_blocks if it exists
            if isinstance(msg_dict, dict) and 'thinking_blocks' in msg_dict:
                if isinstance(msg_dict['thinking_blocks'], list):
                    for block in msg_dict['thinking_blocks']:
                        if isinstance(block, dict) and 'signature' in block:
                            del block['signature']
            
            serializable_messages.append(msg_dict)
        
        print(json.dumps(serializable_messages, indent=2, default=str))

        return response_content

    except Exception as e:
        return f"Error querying database with LLM: {str(e)}"

# Example usage and testing
if __name__ == "__main__":


    # # Test with invalid query
    # test_result = execute_sql_query("data/dev_databases/thrombosis_prediction/thrombosis_prediction.sqlite", "DROP TABLE users")
    # print("Test with invalid query (DROP):")
    # print(json.dumps(test_result, indent=2))

    # TEST_QUERY = "SELECT T1.Diagnosis, T2.Date FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE T1.ID = 30609"
    # db_name = "thrombosis_prediction"

    TEST_QUERY = "SELECT CAST(SUM(CASE WHEN Currency = 'EUR' THEN 1 ELSE 0 END) AS REAL) / SUM(CASE WHEN Currency = 'CZK' THEN 1 ELSE 0 END) FROM customers"
    DB_NAME = "debit_card_specializing"

    print(execute_sql_query_and_return_pretty_results(DB_NAME, TEST_QUERY))


