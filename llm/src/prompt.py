from table_schema import generate_schema_prompt


def generate_comment_prompt(question, sql_dialect, knowledge=None):
    base_prompt = f"-- Using valid {sql_dialect}"
    knowledge_text = " and understanding External Knowledge" if knowledge else ""
    knowledge_prompt = f"-- External Knowledge: {knowledge}" if knowledge else ""

    combined_prompt = (
        f"{base_prompt}{knowledge_text}, answer the following questions for the tables provided above.\n"
        f"-- {question}\n"
        f"{knowledge_prompt}"
    )
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

    combined_prompts = "\n\n".join(
        [schema_prompt, comment_prompt, cot_prompt, instruction_prompt]
    )
    return combined_prompts
