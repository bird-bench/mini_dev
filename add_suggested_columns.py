#!/usr/bin/env python3


import json
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import litellm
import sqlite3
import os
import re
from typing import Set, Tuple
import sqlglot
from sqlglot import parse_one, exp
from sqlglot.expressions import Column, Subquery, CTE, TableAlias, Table
from query_db_schema import get_columns_schema


# Set up logging first
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Set litellm to not print debug info
litellm.set_verbose = False

def get_database_schema(db_id: str, detailed=False) -> str:
    """
    Get the schema for a database using SQLite .schema command.
    
    Args:
        db_id: The database identifier
        
    Returns:
        Schema as a string, or empty string if not found
    """

    if detailed:
        return get_columns_schema(db_id, "all")
    
    # Look for the database file in common locations
    possible_paths = [
        f"data/dev_databases/{db_id}/{db_id}.sqlite"
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        logger.warning(f"Database file not found for db_id: {db_id}")
        return ""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the schema using .schema equivalent
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL")
        schema_parts = []
        for row in cursor.fetchall():
            schema_parts.append(row[0])
        
        conn.close()
        return "\n\n".join(schema_parts)
        
    except Exception as e:
        logger.error(f"Error getting schema for {db_id}: {e}")
        return ""
    


def get_from_tables(expr):
    """Return a list of Table or TableAlias objects in the immediate FROM clause."""
    from_expr = expr.args.get("from")
    if from_expr and hasattr(from_expr, 'this'):
        return [from_expr.this]
    return []

def process_select_statement(select_expr):
    """Process a single SELECT statement to extract its columns with proper table resolution."""
    aliases = {}
    results = set()
    
    # --- Update aliases from FROM clause ---
    for table_expr in get_from_tables(select_expr):
        if isinstance(table_expr, Table):
            table_name = str(table_expr.this) if table_expr.this else str(table_expr)
            if hasattr(table_expr, 'alias') and table_expr.alias:
                alias_name = str(table_expr.alias)
                aliases[alias_name] = table_name
            else:
                aliases[table_name] = table_name

    # --- Handle JOINs ---
    joins = select_expr.args.get("joins", [])
    if joins:
        for join_expr in joins:
            if hasattr(join_expr, 'this'):
                join_table = join_expr.this
                if isinstance(join_table, Table):
                    table_name = str(join_table.this) if join_table.this else str(join_table)
                    if hasattr(join_table, 'alias') and join_table.alias:
                        alias_name = str(join_table.alias)
                        aliases[alias_name] = table_name
                    else:
                        aliases[table_name] = table_name

    # --- Find columns that belong only to this SELECT (not nested subqueries) ---
    # We'll traverse the SELECT arguments manually to avoid picking up subquery columns
    for arg_name in ['expressions', 'where', 'group', 'having', 'order']:
        arg_value = select_expr.args.get(arg_name)
        if arg_value:
            if isinstance(arg_value, list):
                for item in arg_value:
                    columns = find_columns_excluding_subqueries(item)
                    results.update(resolve_columns_with_aliases(columns, aliases, select_expr))
            else:
                columns = find_columns_excluding_subqueries(arg_value)
                results.update(resolve_columns_with_aliases(columns, aliases, select_expr))
    
    return results

def find_columns_excluding_subqueries(expr):
    """Find Column objects but exclude those inside nested SELECT statements."""
    columns = []
    if isinstance(expr, Column):
        columns.append(expr)
    elif hasattr(expr, 'args'):
        for arg_name, arg_value in expr.args.items():
            # Skip if this is a SELECT (subquery)
            if isinstance(arg_value, sqlglot.expressions.Select):
                continue
            if isinstance(arg_value, list):
                for item in arg_value:
                    if not isinstance(item, sqlglot.expressions.Select):
                        columns.extend(find_columns_excluding_subqueries(item))
            elif arg_value and hasattr(arg_value, 'args'):
                columns.extend(find_columns_excluding_subqueries(arg_value))
    return columns

def resolve_columns_with_aliases(columns, aliases, select_expr):
    """Resolve column table names using the aliases."""
    results = set()
    
    for column in columns:
        table = column.table
        name = column.name
        
        if table and str(table) in aliases:
            resolved_table = aliases[str(table)]
        elif table:
            resolved_table = str(table)
        else:
            # For implicit tables, use the single table from FROM if available
            from_tables = get_from_tables(select_expr)
            if len(from_tables) == 1:
                table_obj = from_tables[0]
                
                # Handle different types of table objects
                if isinstance(table_obj, sqlglot.expressions.Subquery):
                    # For subqueries, use the alias name, not the inner SQL
                    if hasattr(table_obj, 'alias') and table_obj.alias and str(table_obj.alias).strip():
                        resolved_table = str(table_obj.alias)
                    else:
                        # For unnamed subqueries, use a descriptive name
                        resolved_table = "unnamed_subquery"
                elif isinstance(table_obj, sqlglot.expressions.Table):
                    # For regular tables, use the table name
                    resolved_table = str(table_obj.this) if table_obj.this else str(table_obj)
                else:
                    # Fallback for other types
                    resolved_table = str(table_obj)
            else:
                resolved_table = "<implicit>"
        
        results.add(f"{resolved_table}.{name}")
    
    return results

def extract_table_columns_recursive(expr, aliases=None):
    """
    Extract table.column pairs by processing each SELECT statement separately.
    """
    results = set()
    
    # Find all SELECT statements (including the main one and subqueries)
    all_selects = [expr] + list(expr.find_all(sqlglot.expressions.Select))
    unique_selects = []
    
    # Remove duplicates while preserving order
    seen = set()
    for select_stmt in all_selects:
        select_id = id(select_stmt)
        if select_id not in seen:
            seen.add(select_id)
            unique_selects.append(select_stmt)
    
    # Process each SELECT statement independently
    for select_stmt in unique_selects:
        if isinstance(select_stmt, sqlglot.expressions.Select):
            results.update(process_select_statement(select_stmt))
    
    return results



def normalize_column_casing(table_columns, db_id):
    """
    Normalize column casing to match the actual database schema using sqlite3 metadata.
    """
    if not table_columns or not db_id:
        return table_columns
    
    # Get table and column info directly from the database
    schema_tables = {}  # table_name_lower -> {'original_name': str, 'columns': {col_lower: col_original}}
    
    db_path = f"data/dev_databases/{db_id}/{db_id}.sqlite"
    if not os.path.exists(db_path):
        return table_columns
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            # Skip sqlite internal tables
            if table_name.startswith('sqlite_'):
                continue
                
            # Get column info using PRAGMA table_info (handles reserved keywords)
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()
            
            column_dict = {}
            for col_info in columns:
                col_name = col_info[1]  # Column name is at index 1
                column_dict[col_name.lower()] = col_name
            
            schema_tables[table_name.lower()] = {
                'original_name': table_name,
                'columns': column_dict
            }
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error getting schema info for {db_id}: {e}")
        return table_columns
    
    # Normalize the extracted table.column pairs
    normalized = set()
    for table_col in table_columns:
        if '.' in table_col:
            table_name, col_name = table_col.split('.', 1)
            table_lower = table_name.lower()
            
            # Strip backticks and quotes from column name for matching
            col_name_clean = col_name.strip('`"[]').strip()
            col_lower = col_name_clean.lower()
            
            if table_lower in schema_tables:
                # Only include columns that actually exist in the schema
                if col_lower in schema_tables[table_lower]['columns']:
                    correct_table = schema_tables[table_lower]['original_name']
                    correct_col = schema_tables[table_lower]['columns'][col_lower]
                    normalized.add(f"{correct_table}.{correct_col}")
                # If column doesn't exist in this table, skip it (it's likely computed)
            # If table doesn't exist in schema, skip it (it's likely a computed subquery)
        else:
            # For columns without table prefix, we can't validate, so skip them
            pass
    
    return normalized

def extract_tables_and_columns_from_sql(sql, db_id=None):
    expression = sqlglot.parse_one(sql, read='sqlite')
    raw_columns = set(extract_table_columns_recursive(expression))
    
    # Normalize casing to match database schema
    if db_id:
        return normalize_column_casing(raw_columns, db_id)
    else:
        return raw_columns

def compare_sql_columns_with_suggestions(ground_truth_columns: set, column_suggestions: str) -> bool:
    """
    Compare ground truth columns with suggested columns.
    Returns True if they match (same set of table.column references).
    """
    if not ground_truth_columns or not column_suggestions:
        return False
    
    # Convert ground truth columns to lowercase for comparison
    sql_columns_lower = {col.lower() for col in ground_truth_columns}
    
    # Parse column suggestions - handle both string and list formats
    suggestion_columns = set()
    
    if isinstance(column_suggestions, list):
        suggestion_parts = column_suggestions
    else:
        # Split by common separators and clean up
        suggestion_parts = re.split(r'[,;\n]', column_suggestions)
    
    for part in suggestion_parts:
        part = str(part).strip() if part else ""
        if part and '.' in part:
            # Direct table.column reference, normalize to lowercase
            suggestion_columns.add(part.lower())
    
    # Compare the sets (both normalized to lowercase)
    return sql_columns_lower == suggestion_columns

def expand_column_suggestions(column_suggestions_str: str, db_id: str, schemas_cache: dict) -> list:
    """
    Expand column suggestions by finding all valid table.column combinations
    where both the table name and column name appear in the original suggestions.
    """
    if not column_suggestions_str or not db_id:
        return []
    
    # Get table and column info directly from the database
    table_columns = {}  # table_name -> set of column_names
    
    db_path = f"data/dev_databases/{db_id}/{db_id}.sqlite"
    if not os.path.exists(db_path):
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables and their columns using PRAGMA table_info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            # Quote table name to handle reserved keywords like 'order'
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()
            column_names = {col[1].lower() for col in columns}  # col[1] is the column name
            table_columns[table_name.lower()] = column_names
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error getting table info for {db_id}: {e}")
        return []
    
    # Parse original suggestions to extract mentioned table and column names
    mentioned_tables = set()
    mentioned_columns = set()
    
    suggestion_parts = re.split(r'[,;\n]', column_suggestions_str.lower())
    for part in suggestion_parts:
        part = part.strip()
        if '.' in part:
            table, column = part.split('.', 1)
            mentioned_tables.add(table.strip())
            mentioned_columns.add(column.strip())
    
    # Start with the original suggestions
    expanded = set()
    
    # Add original table.column suggestions
    for part in suggestion_parts:
        part = part.strip()
        if '.' in part and part.count('.') == 1:
            # Valid table.column format
            expanded.add(part)
    
    # Generate additional expanded combinations
    for table_name, available_columns in table_columns.items():
        if table_name in mentioned_tables:
            for column_name in available_columns:
                if column_name in mentioned_columns:
                    expanded.add(f"{table_name}.{column_name}")
    
    return sorted(list(expanded))

def identify_relevant_columns(question: str, evidence: str, db_id: str, schemas_cache: dict) -> str:

    
    # Get the database schema from cache
    schema = schemas_cache.get(db_id, "")
    schema_section = f"\n\nDatabase Schema:\n{schema}" if schema else ""
    
    prompt = f"""You are given a natural-language question about a database, along with someone's guidance about how to formulate a SQL query to answer the question. The guidance was generated by a human worker who has access to the database schema and contents.

Carefully consider the schema, question, and guidance. 

Your task is to identify any columns from the database schema that are relevant to answering the question, including but not limited to columns that are mentioned or implied in the question or guidance.

Return a comma-separated list of any possibly relevant column names along with their corresponding table names in the format: tablename.columnname. 

- Always include any potential canonical identifier columns that might be needed for joining tables or uniquely identifying records.
- Always include columns whose names closely match key terms and phrasing in the question or guidance.
- If you include a column from one table, you must also include identically named columns from other tables that might be relevant.
- If two columns seem quite similar, include them both.
- If you are unsure which of two similar columns is more relevant, include them both. 
- If you are unsure whether a column might be relevant, include it anyway.

Here is the schema, question, and guidance:

{schema_section}

Question:
{question}

Guidance:
{evidence}

Your response: """

    # print(prompt)

    try:
        response = litellm.completion(
            model="vertex_ai/gemini-2.5-flash",
            messages=[
                {"role": "user", "content": prompt}
            ],
            thinking={"enabled": True, "budget_tokens": 4096},
            temperature=0
        )

        result = response.choices[0].message.content.strip()
        
        return result

    except Exception as e:
        logger.error(f"Error in API call:\n{e}")
        # print("Raw response:\n", response)
        return ""

def identify_relevant_instrucitons(question: str, evidence: str, db_id: str, schemas_cache: dict) -> str:

    
    # Get the database schema from cache
    schema = schemas_cache.get(db_id, "")
    schema_section = f"\n\nDatabase Schema:\n{schema}" if schema else ""
    
    prompt = f"""You are given a natural-language question about a database, along with someone's guidance about how to formulate a SQL query to answer the question. The guidance was generated by a human worker who has access to the database schema and contents.

Carefully consider the schema, question, and guidance. 

Your task is to identify any of the following instructions that might be relevant to producing a correct SQL query.

Return a comma-separated list of numbers corresponding to the relevant instructions from the list below. Return only the numbers, separated by commas.

    1. Use COUNT(DISTINCT ...) when counting unique values.
    2. If asked to calculate a ratio or percentage, always make sure the numerator and denominator are the right way around, based on the question and guidance. If the question or guidance asks for a percentage, remember to multiply by 100.0.
    3. If the question asks for a first name and last name, return them as separate columns.
    4. Your query should only return the columns requested in the question and guidance. Don't include extra columns, even if these were used in joins.
    5. When counting, matching, or grouping individuals, you should retrieve on unique identifier columns, if these exist and it seems reasonable to do so.
    6. Your query must never compare a datetime column directly with a date string. Extract the date part using a date function first.
    7. Double-check that your query contains the same >=, >, <=, < operators as the question and guidance, if any.
    8. Always make sure that the table and column names in your query are consistent with the schema provided.
    9. If there is more than one column or table with a similar name, choose the one that most closely matches the word used in the question.
    10. Very important: always make sure that your query takes into account the guidance provided. If the question or guidance mentions specific columns or filter logic, ensure these are reflected in your query.

Here is the schema, question, and guidance:

{schema_section}

Question:
{question}

Guidance:
{evidence}

Your response: """

    # print(prompt)

    try:
        response = litellm.completion(
            model="vertex_ai/gemini-2.5-flash",
            messages=[
                {"role": "user", "content": prompt}
            ],
            thinking={"enabled": True, "budget_tokens": 4096},
            temperature=0
        )

        result = response.choices[0].message.content.strip()
        
        return result

    except Exception as e:
        logger.error(f"Error in API call:\n{e}")
        # print("Raw response:\n", response)
        return ""



def process_single_item(item: dict, index: int, schemas_cache: dict) -> dict:

    question = item.get("question", "")
    evidence = item.get("evidence", "")
    db_id = item.get("db_id", "")
    
    
    column_suggestions = identify_relevant_columns(question, evidence, db_id, schemas_cache)

    # Create result entry
    result_item = {
        "question_id": item.get("question_id"),
        "db_id": item.get("db_id"),
        "question": question,
        "evidence": evidence,
        "column_suggestions": column_suggestions,
        "difficulty": item.get("difficulty"),
        "exact_match": item.get("exact_match"),
        "index": index,  # For maintaining order
        "predicted_sql": item.get("predicted_sql"),
        "ground_truth_sql": item.get("ground_truth_sql")
    }
    
    return result_item

def process_json_file(input_file: str, output_file: str) -> None:
    
    logger.info(f"Loading data from {input_file}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading input file: {e}")
        return

    # data = [item for item in data if item["exact_match"] == 0]

    data = data[:]
    # data = [item for item in data if item.get("question_id", "") in [25, 28, 83, 169, 192, 465, 584, 595, 682, 896, 902, 906, 928, 944, 955, 959, 1404, 1526]]


    # Pre-load all database schemas to avoid redundant database access
    unique_db_ids = set(item.get("db_id", "") for item in data)
    unique_db_ids.discard("")  # Remove empty db_ids
    
    logger.info(f"Pre-loading schemas for {len(unique_db_ids)} unique databases...")
    schemas_cache = {}
    for db_id in unique_db_ids:
        schema = get_database_schema(db_id)
        schemas_cache[db_id] = schema
        if schema:
            logger.info(f"Loaded schema for {db_id} ({len(schema)} chars)")
        else:
            logger.warning(f"No schema found for {db_id}")

    results = []
    total_items = len(data)

    
    logger.info(f"Processing {total_items} items with threading...")

    # Process items in parallel using ThreadPoolExecutor
    max_workers = 12  # Adjust based on API rate limits
    completed_count = 0

    error_count = 0
    counter_lock = Lock()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(process_single_item, item, i, schemas_cache): i 
            for i, item in enumerate(data)
        }
        
        # Collect results as they complete
        results_dict = {}
        for future in as_completed(future_to_index):
            try:
                result_item = future.result()
                results_dict[result_item["index"]] = result_item
                
                # Update counters thread-safely
                with counter_lock:
                    completed_count += 1

                    column_suggestions = result_item["column_suggestions"]

                
                    if completed_count % 10 == 0:
                        logger.info(f"Completed {completed_count}/{total_items} items")
                        
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                error_count += 1
    
    # Sort results by original index to maintain order
    results = [results_dict[i] for i in sorted(results_dict.keys())]
    
    # Remove the index field as it's no longer needed
    for result in results:
        del result["index"]
    
    
    for i, result in enumerate(results):
        # Parse ground truth SQL to extract table.column references
        ground_truth_sql = result.get("ground_truth_sql", "")
        column_suggestions = result.get("column_suggestions", "")
        db_id = result.get("db_id", "")
        
        # Extract columns from ground truth SQL with proper schema casing
        schema = schemas_cache.get(db_id, "")
        ground_truth_columns = extract_tables_and_columns_from_sql(ground_truth_sql, db_id)
        
        # Parse suggestion columns for comparison and formatting
        suggestion_columns = set()
        suggestion_list = []
        
        # Handle both string and list formats for column_suggestions
        if isinstance(column_suggestions, list):
            suggestion_parts = column_suggestions
        else:
            suggestion_parts = re.split(r'[,;\n]', column_suggestions)
        
        for part in suggestion_parts:
            part = str(part).strip() if part else ""
            if part and '.' in part:
                # Keep original case for display, lowercase for comparison
                suggestion_list.append(part)
                suggestion_columns.add(part.lower())
        
        # Generate expanded column suggestions
        expanded_suggestions = expand_column_suggestions(column_suggestions, db_id, schemas_cache)
        
        # Normalize suggestion columns to match schema casing for display consistency
        normalized_suggestions = []
        for suggestion in suggestion_list:
            # Find matching column in schema with proper casing
            if db_id:
                normalized_col = normalize_column_casing({suggestion}, db_id)
                if normalized_col:
                    normalized_suggestions.extend(normalized_col)
                else:
                    normalized_suggestions.append(suggestion)
            else:
                normalized_suggestions.append(suggestion)
        
        # Normalize expanded suggestions to match schema casing
        # Expanded should always be a superset of original suggestions
        normalized_expanded = []
        if expanded_suggestions:
            if db_id:
                # Get normalized versions of both original and expanded suggestions
                expanded_normalized = normalize_column_casing(set(expanded_suggestions), db_id)
                original_normalized = normalize_column_casing(set(normalized_suggestions), db_id)
                
                # Take the union to ensure expanded is always a superset
                combined_set = expanded_normalized.union(original_normalized)
                normalized_expanded = sorted(list(combined_set))
            else:
                # Take union of expanded and original suggestions
                combined_set = set(expanded_suggestions).union(set(normalized_suggestions))
                normalized_expanded = sorted(list(combined_set))
        
        # Compare ground truth columns with suggested columns
        suggestion_match = compare_sql_columns_with_suggestions(ground_truth_columns, column_suggestions)
        
        # Normalize ground truth columns to lowercase for comparison
        ground_truth_lower = {col.lower() for col in ground_truth_columns}
        
        # Check if suggestions contain all ground truth columns (superset)
        suggestions_contain = ground_truth_lower.issubset(suggestion_columns) if ground_truth_lower else False
        
        # Check if expanded suggestions contain all ground truth columns (superset)
        expanded_columns_set = {col.lower() for col in normalized_expanded}
        expanded_suggestions_contain = ground_truth_lower.issubset(expanded_columns_set) if ground_truth_lower else False
        
        # Recreate the result dictionary with desired field order
        ordered_result = {
            "question_id": result.get("question_id"),
            "db_id": result.get("db_id"),
            "question": result.get("question"),
            "evidence": result.get("evidence"),
            "difficulty": result.get("difficulty"),
            "exact_match": result.get("exact_match"),
            "predicted_sql": result.get("predicted_sql"),
            "ground_truth_sql": result.get("ground_truth_sql"),
            "suggestion_match": suggestion_match,
            "suggestions_contain": suggestions_contain,
            "expanded_suggestions_contain": expanded_suggestions_contain,
            "column_suggestions": sorted(normalized_suggestions),
            "expanded_column_suggestions": sorted(normalized_expanded),
            "ground_truth_columns": sorted(list(ground_truth_columns)),
        }
        
        # Replace the result with the ordered version
        results[i] = ordered_result
 

    # Calculate summary statistics
    total_results = len(results)
    matches = sum(1 for result in results if result.get("suggestion_match", False))
    contains = sum(1 for result in results if result.get("suggestions_contain", False))
    expanded_contains = sum(1 for result in results if result.get("expanded_suggestions_contain", False))
    match_percentage = (matches / total_results * 100) if total_results > 0 else 0
    contain_percentage = (contains / total_results * 100) if total_results > 0 else 0
    expanded_contain_percentage = (expanded_contains / total_results * 100) if total_results > 0 else 0
    
    logger.info("Suggestion matching summary:")
    logger.info(f"  Total results: {total_results}")
    logger.info(f"  Exact matches: {matches} ({match_percentage:.1f}%)")
    logger.info(f"  Suggestions contain ground truth: {contains} ({contain_percentage:.1f}%)")
    logger.info(f"  Expanded suggestions contain ground truth: {expanded_contains} ({expanded_contain_percentage:.1f}%)")

    final_output = results


    

    
    # Save all results
    logger.info(f"Saving results to {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving output file: {e}")
        return
    

def main():
    """Main function to run the suggest columns extraction"""
    input_file = "generated_sql_results_evaluation.json"
    output_file = "add_suggested_columns_results.json"
    
    # Check if input file exists
    if not Path(input_file).exists():
        logger.error(f"Input file {input_file} not found!")
        return

    process_json_file(input_file, output_file)
    logger.info("Analysis complete!")

if __name__ == "__main__":
    main()