import sqlite3
import json
import csv
from pathlib import Path

def get_column_descriptions(db_path):
    """Get column descriptions from CSV files in database_description directory."""
    db_dir = db_path.parent
    desc_dir = db_dir / "database_description"
    
    descriptions = {}
    
    if not desc_dir.exists():
        return descriptions
    
    # Read all CSV files in the description directory
    for csv_file in desc_dir.glob("*.csv"):
        table_name = csv_file.stem  # filename without extension
        table_descriptions = {}
        
        try:
            # Try different encodings, starting with utf-8-sig which handles BOM automatically
            for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(csv_file, 'r', encoding=encoding) as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            original_col_name = row.get('original_column_name', '').strip()
                            col_description = row.get('column_description', '').strip()
                            value_description = row.get('value_description', '').strip()
                            
                            if original_col_name:
                                table_descriptions[original_col_name] = {
                                    'description': col_description,
                                    'value_description': value_description
                                }
                    break  # Success, exit encoding loop
                except UnicodeDecodeError:
                    continue  # Try next encoding
            
            descriptions[table_name] = table_descriptions
        except (OSError, csv.Error) as e:
            print(f"    Warning: Could not read {csv_file}: {e}")
    
    return descriptions

def get_sample_values(cursor, table_name, column_name):
    """Get the 5 most frequent values for a column."""
    try:
        # Quote both table and column names to handle reserved keywords and special characters
        query = f'SELECT "{column_name}", COUNT(*) as freq FROM "{table_name}" WHERE "{column_name}" IS NOT NULL GROUP BY "{column_name}" ORDER BY freq DESC LIMIT 5'
        cursor.execute(query)
        results = cursor.fetchall()
        sample_values = []
        for row in results:
            value_str = str(row[0])
            # Truncate if longer than 30 characters
            if len(value_str) > 30:
                value_str = value_str[:30] + "..."
            sample_values.append(value_str)
        return sample_values
    except sqlite3.Error:
        return []

def get_table_columns(db_path):
    """Get all table names and their columns from a SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get column descriptions from CSV files
    column_descriptions = get_column_descriptions(db_path)
    
    # Get all table names, excluding SQLite system tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()
    
    db_schema = {}
    
    for table in tables:
        table_name = table[0]
        # Get column info for each table (quote table name to handle reserved keywords)
        cursor.execute(f"PRAGMA table_info(\"{table_name}\");")
        columns = cursor.fetchall()
        
        # Create nested dict with table name as key and columns as nested dict
        # Column info format: [cid, name, type, notnull, dflt_value, pk]
        table_columns = {}
        table_desc = column_descriptions.get(table_name, {})
        
        for col in columns:
            col_name = col[1]
            col_desc_info = table_desc.get(col_name, {})
            sample_values = get_sample_values(cursor, table_name, col_name)
            
            col_info = {
                "type": col[2],
                "nullable": not bool(col[3]),
                "default_value": col[4],
                "primary_key": bool(col[5]),
                "description": col_desc_info.get('description', '') if isinstance(col_desc_info, dict) else col_desc_info,
                "sample_values": sample_values,
                "value description": col_desc_info.get('value_description', '') if isinstance(col_desc_info, dict) else ''
            }
            table_columns[col_name] = col_info
        
        db_schema[table_name] = table_columns
    
    conn.close()
    return db_schema

def main():
    # Path to the dev_databases directory
    dev_databases_path = Path("data/dev_databases")
    
    if not dev_databases_path.exists():
        print(f"Directory {dev_databases_path} does not exist!")
        return
    
    result = {}
    
    # Loop through each subdirectory
    for subdir in dev_databases_path.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('.'):
            db_name = subdir.name
            sqlite_file = subdir / f"{db_name}.sqlite"
            
            print(f"Processing database: {db_name}")
            
            if sqlite_file.exists():
                try:
                    db_schema = get_table_columns(sqlite_file)
                    result[db_name] = db_schema
                    print(f"  Found {len(db_schema)} columns")
                except sqlite3.Error as e:
                    print(f"  Error processing {db_name}: {e}")
                    result[db_name] = {}
            else:
                print(f"  SQLite file not found: {sqlite_file}")
                result[db_name] = {}
    
    # Save to JSON file
    output_file = "database_columns_schema.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    print(f"Processed {len(result)} databases")

if __name__ == "__main__":
    main()