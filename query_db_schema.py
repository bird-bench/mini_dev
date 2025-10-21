import json
import sys


def load_schema(schema_file="database_columns_schema.json"):
    """Load the database schema from JSON file."""
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file '{schema_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file: {e}")
        sys.exit(1)


def parse_column_spec(column_spec):
    """Parse table.column specification into table and column parts."""
    if '.' not in column_spec:
        print(f"Error: Invalid column specification '{column_spec}'. Expected format: table.column")
        return None, None
    
    parts = column_spec.split('.', 1)  # Split only on the first dot
    return parts[0], parts[1]


def query_schema(db_name, column_specs, schema_data):
    """Query schema information for specified database and columns."""
    if db_name not in schema_data:
        print(f"Error: Database '{db_name}' not found in schema.")
        available_dbs = list(schema_data.keys())
        print(f"Available databases: {', '.join(available_dbs)}")
        return {}
    
    db_schema = schema_data[db_name]
    result = {}
    
    # Handle "all" case - return all columns for all tables
    if column_specs == "all":
        return db_schema
    
    for column_spec in column_specs:
        table_name, column_name = parse_column_spec(column_spec)
        
        if table_name is None or column_name is None:
            continue
        
        if table_name not in db_schema:
            print(f"Warning: Table '{table_name}' not found in database '{db_name}'.")
            available_tables = list(db_schema.keys())
            print(f"Available tables: {', '.join(available_tables)}")
            continue
        
        table_schema = db_schema[table_name]
        
        if column_name not in table_schema:
            print(f"Warning: Column '{column_name}' not found in table '{table_name}'.")
            available_columns = list(table_schema.keys())
            print(f"Available columns in '{table_name}': {', '.join(available_columns)}")
            continue
        
        # Create nested structure in result
        if table_name not in result:
            result[table_name] = {}
        
        result[table_name][column_name] = table_schema[column_name]
    
    return result


def prettify_column_info(result):
    """Format schema information as a nicely formatted string."""
    if not result:
        return "No valid columns found."
    
    output = []
    
    for table_name, columns in result.items():
        output.append(f"\n\nTable: {table_name}")
        output.append("-" * 30)
        
        for column_name, column_info in columns.items():

            output.append(f"\n  Column: {column_name}")
            # if column_info.get('description'):
            #     output.append(f"    Description: {column_info['description']}")
            if column_info.get('description', "") not in ["", column_name]:
                output.append(f"    Additional Description: {column_info['description']}")
            else: 
                output.append("    Additional Description: None")
            output.append(f"    Type: {column_info.get('type', 'N/A')}")
            output.append(f"    Primary Key: {column_info.get('primary_key', False)}")
            output.append(f"    Nullable: {column_info.get('nullable', 'N/A')}")
            output.append(f"    Default: {column_info.get('default_value', 'None')}")
            

            
            # if column_info.get('value description'):
            #     output.append(f"    Additional information: {column_info['value description']}")

            sample_values = column_info.get('sample_values', [])
            if sample_values:
                output.append(f"    Sample Values: {', '.join(sample_values[:5])}")
    
    return '\n'.join(output)

def get_columns_schema(db_name, column_specs, schema_file="database_columns_schema.json"):
    """
    Get formatted column information for specified database and columns.
    
    Args:
        db_name (str): Name of the database
        column_specs (list): List of table.column specifications
        schema_file (str): Path to the schema JSON file
    
    Returns:
        str: Formatted column information
    """
    schema_data = load_schema(schema_file)
    result = query_schema(db_name, column_specs, schema_data)
    return prettify_column_info(result)

if __name__ == "__main__":
    # Example usage
    print(get_columns_schema("debit_card_specializing", ["yearmonth.Date"]))