#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BIRD dataset preprocessing script, convert to verl format
"""

import json
import os
import argparse
import pandas as pd
from tqdm import tqdm

def process_bird_data(json_file, output_file):
    """Process BIRD dataset"""
    
    # Read original data
    with open(json_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    print(f"Original data count: {len(raw_data)}")
    
    processed_data = []
    failed_count = 0
    
    for idx, item in enumerate(tqdm(raw_data, desc="Processing data")):
        try:
            # Check required fields
            if not all(key in item for key in ['question', 'gt_sql', 'db_id']):
                print(f"Skip sample {idx}: missing required fields")
                failed_count += 1
                continue
            
            prompt_content = item['input_seq']
            response_content = item.get('output_seq', item.get('response', ''))
            # Build verl format data
            verl_item = {
                "prompt": prompt_content,
                "response": response_content
            }
            
            processed_data.append(verl_item)
            
        except Exception as e:
            print(f"Error processing sample {idx}: {e}")
            failed_count += 1
            continue
    
    print(f"Processing completed: success {len(processed_data)}, failed {failed_count}")
    
    # Save processed data
    df = pd.DataFrame(processed_data)
    df.to_parquet(output_file, index=False)
    
    print(f"Data saved to: {output_file}")
    print(f"Final data count: {len(df)}")
    
    return len(df)


def main():
    parser = argparse.ArgumentParser(description="Process BIRD dataset to verl format")
    parser.add_argument("--input_json", 
                       default="/path/to/split_train.json",
                       help="Input JSON file path")
    parser.add_argument("--output_file", 
                       default="/path/to/train_bird.parquet",
                       help="Output parquet file path")
    
    # parser.add_argument("--input_json", 
    #                    default="/path/to/split_val.json",
    #                    help="Input JSON file path")
    # parser.add_argument("--output_file", 
    #                    default="/path/to/val_bird.parquet",
    #                    help="Output parquet file path")
    
    args = parser.parse_args()
    
    # Check input file
    if not os.path.exists(args.input_json):
        print(f"Error: Input file does not exist {args.input_json}")
        return
    

    # Create output directory
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    
    # Process data
    process_bird_data(args.input_json, args.output_file)


if __name__ == "__main__":
    main()