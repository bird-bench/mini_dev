import json
import random
from collections import defaultdict

def load_jsonl(file_path):
    # Check file extension to decide reading method
    if file_path.endswith('.jsonl'):
        # JSONL format: one JSON object per line
        data = []
        with open(file_path, "r") as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    data.append(json.loads(line))
        return data
    else:
        # JSON format: JSON array
        with open(file_path, "r") as file:
            return json.load(file)

def split_json_data(input_file, train_file, val_file, val_ratio=0.1):
    """
    Split JSON data into training and validation sets
    
    Args:
        input_file: Input JSON file path
        train_file: Training set output file path
        val_file: Validation set output file path
        val_ratio: Validation set ratio, default 0.1 (10%)
    """
    
    # Load original data
    data = load_jsonl(input_file)
    
    # Group by db_id
    db_groups = defaultdict(list)
    for item in data:
        db_groups[item['db_id']].append(item)
    
    # Get all db_ids
    all_db_ids = list(db_groups.keys())
    random.shuffle(all_db_ids)
    
    # Calculate how many db_ids needed for validation set
    total_items = len(data)
    target_val_size = int(total_items * val_ratio)
    
    # Select db_ids for validation set, ensuring validation set size is close to target ratio
    val_db_ids = []
    val_items_count = 0
    
    for db_id in all_db_ids:
        if val_items_count + len(db_groups[db_id]) <= target_val_size * 1.5:  # Allow some flexibility
            val_db_ids.append(db_id)
            val_items_count += len(db_groups[db_id])
        
        # Stop adding if already close to target size
        if val_items_count >= target_val_size:
            break
    
    # If validation set is too small, continue adding db_ids
    if val_items_count < target_val_size * 0.8:
        remaining_db_ids = [db_id for db_id in all_db_ids if db_id not in val_db_ids]
        for db_id in remaining_db_ids:
            val_db_ids.append(db_id)
            val_items_count += len(db_groups[db_id])
            if val_items_count >= target_val_size:
                break
    
    # Split data
    train_data = []
    val_data = []
    
    for db_id, items in db_groups.items():
        if db_id in val_db_ids:
            val_data.extend(items)
        else:
            train_data.extend(items)
    
    # Shuffle data order
    random.shuffle(train_data)
    random.shuffle(val_data)
    
    # Save training set
    with open(train_file, 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    
    # Save validation set
    with open(val_file, 'w', encoding='utf-8') as f:
        json.dump(val_data, f, ensure_ascii=False, indent=2)
    
    # Print statistics
    print(f"Total original data: {len(data)}")
    print(f"Training data count: {len(train_data)} ({len(train_data)/len(data)*100:.1f}%)")
    print(f"Validation data count: {len(val_data)} ({len(val_data)/len(data)*100:.1f}%)")
    print(f"Total database count: {len(all_db_ids)}")
    print(f"Training database count: {len(all_db_ids) - len(val_db_ids)}")
    print(f"Validation database count: {len(val_db_ids)}")
    print(f"Validation databases: {val_db_ids}")
    
    # Verify database IDs are disjoint
    train_db_ids = set()
    val_db_ids_check = set()
    
    for item in train_data:
        train_db_ids.add(item['db_id'])
    
    for item in val_data:
        val_db_ids_check.add(item['db_id'])
    
    intersection = train_db_ids.intersection(val_db_ids_check)
    if intersection:
        print(f"Warning: Training and validation sets have same database IDs: {intersection}")
    else:
        print("✅ Training and validation sets have completely disjoint database IDs")

if __name__ == "__main__":
    # Set random seed to ensure reproducible results
    random.seed(42)
    
    # File paths
    input_file = "/path/to/train.json"
    train_file = "/path/to/split_train.json"
    val_file = "/path/to/split_val.json"

    # Execute split
    split_json_data(input_file, train_file, val_file)