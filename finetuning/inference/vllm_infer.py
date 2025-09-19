#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import argparse
import jsonlines
from typing import List, Dict
import torch
from vllm import LLM, SamplingParams

# ----------------------------
# Helpers
# ----------------------------
def load_jsonl(path: str) -> List[Dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for obj in jsonlines.Reader(f):
            items.append(obj)
    return items

def write_jsonl(path: str, items: List[Dict]):
    with open(path, "w", encoding="utf-8") as f:
        for x in items:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

def write_index_json_map(path: str, pred_sql_list: List[str]):
    data = {str(i): s for i, s in enumerate(pred_sql_list)}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
def batches(seq, bs):
    for i in range(0, len(seq), bs):
        yield seq[i:i+bs]

# ----------------------------
# SQL extraction 
# ----------------------------
def sql_response_extract(response_string):
    """
    1. Attempt to extract the first code block labeled with ```sqlite.
    2. If none found, attempt to extract the first code block labeled with ```sql.
    3. If none found in either, return an empty string.

    Returns:
        A single string (the SQL statement/code) or "" if none found.
    """
    # Pattern to match ```sqlite ... ```
    sqlite_pattern = re.compile(
        r"```[ \t]*sqlite\s*([\s\S]*?)```",  
        re.IGNORECASE
    )
    # Pattern to match ```sqlite ... ```
    mysql_pattern = re.compile(
        r"```[ \t]*mysql\s*([\s\S]*?)```",  
        re.IGNORECASE
    )
    postgresql_pattern = re.compile(
        r"```[ \t]*postgresql\s*([\s\S]*?)```",  
        re.IGNORECASE
    )
    # Pattern to match ```sql ... ```
    sql_pattern = re.compile(
        r"```[ \t]*sql\s*([\s\S]*?)```",
        re.IGNORECASE
    )

    # 1) Try matching ```sqlite for the first block
    match_sqlite = sqlite_pattern.search(response_string)
    if match_sqlite:
        # match_sqlite.group(1) contains the code between the backticks
        return match_sqlite.group(1).strip()

    # 2) If no sqlite block found, try matching ```sql
    match_sql = sql_pattern.search(response_string)
    if match_sql:
        return match_sql.group(1).strip()

    match_mysql = mysql_pattern.search(response_string)
    if match_mysql:
        return match_mysql.group(1).strip()

    match_postgresql = postgresql_pattern.search(response_string)
    if match_postgresql:
        return match_postgresql.group(1).strip()

    
    # 3) If neither found, return an empty string
    return response_string.replace("```sql","").replace("```sqlite","").replace("```","")


# ----------------------------
# Inference
# ----------------------------
def run_infer(
    model_path: str,
    prompt_items: List[Dict],
    batch_size: int = 32,
    max_model_len: int = 15000,
    temperature: float = 0.0,
) -> List[str]:
    """
    Returns raw generated texts aligned with prompt_items.
    Each prompt item must contain a 'prompt' string.
    """
    # heuristic tp / util
    mp = model_path.lower()
    if "72b" in mp or "70b" in mp:
        tp_size, gpu_util = 4, 0.95
    elif "gemma3" in mp or "phi-4" in mp:
        tp_size, gpu_util = 2, 0.95
    else:
        tp_size, gpu_util = 1, 0.90

    llm = LLM(
        model=model_path,
        tensor_parallel_size=tp_size,
        trust_remote_code=True,
        gpu_memory_utilization=gpu_util,
        max_model_len=max_model_len,
        disable_custom_all_reduce=True,
    )
    tok = llm.get_tokenizer()

    sampling = SamplingParams(
        temperature=temperature,
        top_p=1.0,
        max_tokens=3000,
        presence_penalty=0.0,
        frequency_penalty=0.0,
        stop=["</FINAL_ANSWER>"],
        stop_token_ids=[tok.eos_token_id],
    )

    use_chat_template = ("sqlcoder-7b-2" not in mp)
    prompts = [it["prompt"] for it in prompt_items]
    generations = []

    for chunk in batches(prompts, batch_size):
        if use_chat_template:
            conversations = [
                tok.apply_chat_template(
                    [{"role": "user", "content": p}],
                    tokenize=False,
                    add_generation_prompt=True,
                )
                for p in chunk
            ]
        else:
            conversations = chunk

        with torch.no_grad():
            outs = llm.generate(conversations, sampling)

        for o in outs:
            generations.append(o.outputs[0].text)

    return generations

# ----------------------------
# Main: vLLM inference + postprocess
# ----------------------------
def main():
    ap = argparse.ArgumentParser("vLLM inference + SQL postprocess")
    ap.add_argument("--model_path", type=str, required=True)
    ap.add_argument("--prompt_path", type=str, required=True, help="JSONL with 'prompt' field")
    ap.add_argument("--output_path", type=str, required=True,
                    help="If endswith .json -> write {'0': 'sql', ...}; if .jsonl -> write per-line JSONL")
    ap.add_argument("--raw_output_path", type=str, default="", help="(optional) save raw responses JSONL")
    ap.add_argument("--gpu", type=str, default="0")
    ap.add_argument("--batch_size", type=int, default=50)
    ap.add_argument("--max_token_length", type=int, default=15000)
    ap.add_argument("--temperature", type=float, default=0.0)
    args = ap.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu

    items = load_jsonl(args.prompt_path)
    assert len(items) > 0 and "prompt" in items[0], "Input must be JSONL with a 'prompt' field."

    # 1) inference
    raw_texts = run_infer(
        model_path=args.model_path,
        prompt_items=items,
        batch_size=args.batch_size,
        max_model_len=args.max_token_length,
        temperature=args.temperature,
    )

    # 2) (optional) dump raw
    if args.raw_output_path:
        raw_dump = []
        for it, txt in zip(items, raw_texts):
            row = dict(it)
            row["response"] = txt
            raw_dump.append(row)
        write_jsonl(args.raw_output_path, raw_dump)

    # 3) postprocess -> pred_sql list
    pred_sql_list = []
    final_rows = []
    for it, txt in zip(items, raw_texts):
        sql = sql_response_extract(txt) or ""
        pred_sql_list.append(sql)
        row = dict(it)
        row["response"] = txt
        row["pred_sql"] = sql
        row.pop("prompt", None)
        final_rows.append(row)

    # 4) write output: json map or jsonl
    if args.output_path.lower().endswith(".json"):
        write_index_json_map(args.output_path, pred_sql_list)
    else:
        write_jsonl(args.output_path, final_rows)

    print(f"[Done] {len(final_rows)} predictions -> {args.output_path}")
    if args.raw_output_path:
        print(f"[Raw ] {len(final_rows)} raw -> {args.raw_output_path}")

if __name__ == "__main__":
    main()
