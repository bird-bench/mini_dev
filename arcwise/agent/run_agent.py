import logging
import traceback

from dotenv import load_dotenv
from openai.types.chat import ChatCompletion
import litellm

from .execute_sql import (
    EXECUTE_SQL_TOOL,
    ExecuteSQLToolArguments,
    ExecuteSQLToolResult,
    execute_sql,
    execute_sql_tool,
)
from .prompts import SYSTEM_PROMPT
from .utils import (
    BIRDQuestion,
    ChatCompletionMessageParam,
    EvaluationResult,
    SQLContext,
)

load_dotenv()


MAX_ITERATIONS = 10
LITELLM_RETRIES = 3
LITELLM_TIMEOUT = 60.0


async def agent_loop(
    question: BIRDQuestion,
    sql_context: SQLContext,
) -> tuple[list[ChatCompletionMessageParam], ExecuteSQLToolResult]:
    user_message = question.question.strip()
    if question.evidence:
        # TODO: need to flag this as potentially inaccurate
        user_message += "\nContext: " + question.evidence.strip()

    if predictions := question.llama_predictions:
        predicted_columns = ""
        for col in predictions.input_columns:
            predicted_columns += f"- {col.column}"
            # if col.description:
            #     predicted_columns += f" ({col.description})"
            predicted_columns += "\n"

        # Logit-based
        # sorted_input_column_logits = sorted(predictions.input_column_logits.items(), key=lambda x: x[1], reverse=True)
        # for key, value in sorted_input_column_logits:
        #     if value < -1:
        #         break
        #     predicted_columns += f"- {key}: "
        #     if value >= 1:
        #         predicted_columns += "high relevance"
        #     else:
        #         predicted_columns += "medium relevance"
        #     predicted_columns += "\n"

        user_message += f"""
Hint: The following columns are most relevant to the question:
{predicted_columns}
"""
        user_message += """
When you have the final answer, run `execute_sql` with a `query_identifier` of "final_answer" with all information in one single query.
I need final_answer to have exactly the following column types:
"""
        for i, col in enumerate(predictions.output_types):
            user_message += f"\n{i+1}. {col.type.upper()}: {col.description}"

        # TODO: try injecting predictions.input_columns and/or predictions.input_column_logits

    message_log: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\n" + (question.filtered_schema or sql_context.db_schema),
        },
        {"role": "user", "content": user_message},
    ]
    final_sql_result = ExecuteSQLToolResult(error="execute_sql was never called")

    logger_name = f"{question.db_id}"
    if question.question_id:
        logger_name += f" #{question.question_id}"
    logger = logging.getLogger(logger_name)

    logger.info(f"Running agent: {user_message}")

    sql_by_exec_result_id: dict[str, str] = {}
    for _ in range(MAX_ITERATIONS):
        response: ChatCompletion = await litellm.acompletion(
            model=sql_context.model,
            # WARNING: LiteLLM mutates the message log for Claude (to extract the system prompt)
            messages=list(message_log),  # type: ignore
            tools=[EXECUTE_SQL_TOOL],
            drop_params=True,
            temperature=0.0,
            timeout=60.0,
            max_retries=3,
        )
        message = response.choices[0].message
        if message.content:
            logger.info(f"Assistant response: {message.content}")
        message_log.append(message.model_dump())  # type: ignore

        if not (tool_calls := getattr(message, "tool_calls", None)):
            # Agent is finished
            break

        for tool_call in tool_calls:
            try:
                arguments = ExecuteSQLToolArguments.model_validate_json(
                    tool_call.function.arguments
                )
                logger.info(f"Executing SQL: {arguments.query_description}\n{arguments.sql}")
                gpt_result, tool_result = await execute_sql_tool(
                    arguments, sql_by_exec_result_id, sql_context
                )
                logger.info(f"SQL result {gpt_result}")
                if tool_result.exec_result_id and tool_result.sql:
                    sql_by_exec_result_id[tool_result.exec_result_id] = tool_result.sql
                    final_sql_result = tool_result
                # TODO: heuristically stop if this result is marked as 'final_answer'?
            except Exception as e:
                gpt_result = f"Error parsing execute_sql arguments: {e}"
                logger.warning(gpt_result)
                tool_result = ExecuteSQLToolResult(error=gpt_result)

            message_log.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": gpt_result}
            )

    return message_log, final_sql_result


async def evaluate_question(
    index: int, question: BIRDQuestion, sql_context: SQLContext
) -> tuple[int, BIRDQuestion, EvaluationResult]:
    try:
        message_log, final_sql_result = await agent_loop(question, sql_context)
    except Exception as e:
        print(f"Unexpected agent error: {e}")
        return (
            index,
            question,
            EvaluationResult(
                predicted_sql="",
                predicted_result="Agent error: " + str(e),
                message_log=[],
            ),
        )

    if question.SQL:
        try:
            _cols, golden_result = await execute_sql(question.SQL, sql_context)
        except Exception:
            print(f"Error: golden SQL failed: {question.SQL}")
            print(f"{question.db_id}: {question.question}")
            traceback.print_exc()
            golden_result = []

        if not final_sql_result.rows or not final_sql_result.sql:
            predicted_result = final_sql_result.error or "Unknown error"
            ex_match = False
            final_sql = ""
        else:
            predicted_result = final_sql_result.rows
            ex_match = set(map(tuple, predicted_result)) == set(map(tuple, golden_result))
            final_sql = final_sql_result.sql

        return (
            index,
            question,
            EvaluationResult(
                predicted_sql=final_sql,
                predicted_result=predicted_result,
                message_log=message_log,
                ex_match=ex_match,
                golden_result=golden_result,
            ),
        )

    return (
        index,
        question,
        EvaluationResult(
            predicted_sql=final_sql_result.sql or "",
            message_log=message_log,
            predicted_result=final_sql_result.rows
            or final_sql_result.error
            or "Could not generate SQL",
        ),
    )
