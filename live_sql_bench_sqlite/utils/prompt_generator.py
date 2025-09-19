import json
import os, sys
import argparse
import logging
from tqdm import tqdm

from prompt.baseline import assistant_prompt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache dictionaries
_schema_cache = {}
_column_meanings_cache = {}
_external_knowledge_cache = {}

# Utility functions
def load_jsonl(file_path):
    with open(file_path, "r") as file:
        return [json.loads(line) for line in file]


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def write_prompts(prompts, data_list, prompt_path):
    create_directory(os.path.dirname(prompt_path))
    with open(prompt_path, "w") as f:
        for i, instance in enumerate(data_list):
            instance["prompt"] = prompts[i]
            f.write(json.dumps(instance, ensure_ascii=False) + "\n")


def load_db_data_if_needed(db_name: str, data_path_base: str):
    """Loads schema, column meanings, and knowledge for a db if not already cached."""

    if db_name not in _column_meanings_cache:
        db_folder_path = os.path.join(data_path_base, db_name)
        # Load Schema
        schema_path = os.path.join(db_folder_path, f"{db_name}_schema.txt")
        # print(f"Schema path: {schema_path}")
        
        try:
            print(f"Loading schema for {db_name} from {schema_path}")
            with open(schema_path, "r") as f:
                _schema_cache[db_name] = f.read()
            print(f"Loaded schema for {db_name} from {schema_path}")
            logger.debug(f"Loaded schema for {db_name}")
        except Exception as e:
            # logger.error(f"Failed to load schema for {db_name} from {schema_path}: {e}")
            print(f"Failed to load schema for {db_name} from {schema_path}: {e}")
            _schema_cache[db_name] = str(e)

        # Load Column Meanings
        col_mean_path = os.path.join(db_folder_path, f"{db_name}_column_meaning_base.json")
        try:
            with open(col_mean_path, "r") as f:
                meanings = json.load(f)
            # Case-insensitive keys
            _column_meanings_cache[db_name] = {k.lower(): v for k, v in meanings.items()}
            logger.debug(f"Loaded column meanings for {db_name}")
        except Exception as e:
            logger.error(f"Failed to load column meanings for {db_name} from {col_mean_path}: {e}")
            _column_meanings_cache[db_name] = {}

        # Load External Knowledge
        kb_path = os.path.join(db_folder_path, f"{db_name}_kb.jsonl")
        try:
            kb = {}
            with open(kb_path, "r") as f:
                for line in f:
                    knowledge = json.loads(line.strip())
                    kb[knowledge["knowledge"]] = knowledge
            _external_knowledge_cache[db_name] = kb
            logger.debug(f"Loaded external knowledge for {db_name}")
        except Exception as e:
            logger.error(f"Failed to load external knowledge for {db_name} from {kb_path}: {e}")
            _external_knowledge_cache[db_name] = {}


def generate_prompts(data_list, data_path_base, prompt_type):
    """Generate prompts for the data list.
    
    Args:
        data_list: List of data instances
        data_path_base: Base path for data files
        prompt_type: Type of prompt to generate (currently only supports "assistant")
    """
    prompt_list = []
    final_data_list = []
    

    # Use tqdm to show progress while generating prompts
    for data in tqdm(data_list, desc="Generating prompts"):
        if prompt_type == "assistant":
            # Load additional data needed for the prompt
            db_name = data["selected_database"]
            load_db_data_if_needed(db_name, data_path_base)
            
            # Add loaded data to the instance
            data["schema"] = _schema_cache.get(db_name, {})
            data["column_meanings"] = _column_meanings_cache.get(db_name, {})
            data["knowledge"] = _external_knowledge_cache.get(db_name, {})
            
            prompt_list.append(assistant_prompt(data))
            final_data_list.append(data)
        else:
            raise ValueError(f"Invalid prompt type: {prompt_type}")
    return prompt_list, final_data_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate prompts for the SQL assistant task."
    )
    parser.add_argument("--data_path", type=str, required=True, help="Path to the data file.")
    parser.add_argument(
        "--prompt_path", type=str, required=True, help="Path to save the generated prompts."
    )
    parser.add_argument(
        "--prompt_type",
        type=str,
        default="assistant",
        help="Type of prompt to generate (currently only supports 'assistant').",
    )
    parser.add_argument(
        "--data_path_base",
        type=str,
        required=True,
        help="Base path containing database folders (each with schema.txt, column_meaning_base.json, and kb.jsonl)."
    )
    args = parser.parse_args()

    # Load the data from the JSONL file
    data_list = load_jsonl(args.data_path)

    # Generate prompts
    prompt_list, final_data_list = generate_prompts(
        data_list, 
        args.data_path_base,
        args.prompt_type
    )

    # Write prompts to file
    write_prompts(prompt_list, final_data_list, args.prompt_path)
    print(f"Generated {len(prompt_list)} prompts.")
    print("Prompts generated successfully.")