import json


def assistant_prompt(json_data):
    """Generate a prompt for the CoT SQL assistant.
    
    Args:
        json_data (dict): Dictionary containing:
            - query: The user's query
            - selected_database: Database name
            - schema: Database schema as text (from schema.txt)
            - column_meanings: Column meanings dictionary with case-insensitive keys
            - knowledge: External knowledge dictionary keyed by knowledge name
    """
    query = json_data["query"]
    db_name = json_data["selected_database"]
    
    # Get schema (already loaded as text)
    schema = json_data.get("schema", "Schema not available")
    
    # Get column meanings (already loaded as dict with case-insensitive keys)
    column_meanings = json_data.get("column_meanings", {})
    col_meanings_str = json.dumps(column_meanings, indent=2)
    
    # Get knowledge base (already loaded as dict)
    knowledge = json_data.get("knowledge", {})
    visible_kbs = []
    for k_info in knowledge.values():
        visible_fields = ["id", "knowledge", "description", "definition"]
        visible_kbs.append({k: k_info[k] for k in visible_fields if k in k_info})
    knowledge_str = json.dumps(visible_kbs, indent=2)
    
    # Build the full prompt using the template
    return f"""# Database Schema:
{schema}

# Column Meanings:
{col_meanings_str}

# External Knowledge:
{knowledge_str}

# User Task:
{query}

Generate the correct SQLite to handle the user task above:
(FORMAT: You should enclose your final SQLite in '```sqlite\n[Your Generated SQLs]\n```' in the end. Could use semicolon to separate multiple statements.)

# Your Generated SQL: 
```sqlite"""