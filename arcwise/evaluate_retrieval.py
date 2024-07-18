import json
import math
import os
import shelve
from contextlib import aclosing
from dataclasses import dataclass
from functools import partial

import asyncio
import click
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.vector_stores.types import VectorStoreQuery
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.embeddings.bedrock import Models as BedrockModels
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModeModel
from llama_index.embeddings.voyageai import VoyageEmbedding
from llama_index.vector_stores.duckdb import DuckDBVectorStore
from tqdm.asyncio import tqdm
from transformers import AutoTokenizer

from .ddl import get_table_ddl
from .sql_references import extract_sql_references
from .typedefs import Table
from .utils import (
    BIRDQuestion,
    coro,
    load_database_metadata,
    load_questions,
    run_with_concurrency,
)

load_dotenv()

EMBED_MODELS: dict[str, BaseEmbedding] = {
    "gemini": GeminiEmbedding("models/text-embedding-004"),
    "bedrock": BedrockEmbedding(
        model_name=BedrockModels.COHERE_EMBED_ENGLISH_V3, region_name="us-west-2"
    ),
    "openai_large": OpenAIEmbedding(model=OpenAIEmbeddingModeModel.TEXT_EMBED_3_LARGE),
    "openai_small": OpenAIEmbedding(model=OpenAIEmbeddingModeModel.TEXT_EMBED_3_SMALL),
    "voyage": VoyageEmbedding(model_name="voyage-code-2"),
}
QUERY_EMBED_MODELS = {
    # Gemini doesn't do the task_type switching automatically :\
    "gemini": GeminiEmbedding("models/text-embedding-004", task_type="question_answering"),
}
MODEL_LIMITS = {
    "gemini": 8000,
    "bedrock": 8000,
    "openai_large": 20000,
    "openai_small": 20000,
    "voyage": 40000,
}


def _get_document(table: Table, method: str | None) -> str:
    if method == "description":
        assert table.ai_description
        return table.ai_description
    return get_table_ddl(table)


@click.command()
@click.option("--questions-file", help="Path to questions JSON", required=True)
@click.option("--metadata-file", help="Path to JSON metadata", required=True)
@click.option("--persist-dir", help="Persistence path", default="retrieval_storage")
@click.option("--model", help="Model identifier", required=True)
@click.option("--method", help="Method")
@click.option("--context-limit", help="Simulated context limit", default=8000)
@coro
async def main(
    questions_file: str,
    metadata_file: str,
    persist_dir: str,
    model: str,
    method: str | None,
    context_limit: int,
) -> None:
    metadata = load_database_metadata(metadata_file)
    dumb_splitter = TokenTextSplitter(chunk_size=999999)
    embed_model = EMBED_MODELS[model]
    model_limit = MODEL_LIMITS[model]
    test_embedding = await embed_model.aget_query_embedding("test")

    ddb_path = model + ("." + method if method else "") + ".duckdb"
    if os.path.exists(persist_dir + "/" + ddb_path):
        store = DuckDBVectorStore.from_local(persist_dir + "/" + ddb_path)
        existing_ids = set(
            store.query(VectorStoreQuery(query_embedding=test_embedding, similarity_top_k=9999)).ids
            or []
        )
    else:
        store = DuckDBVectorStore(ddb_path, persist_dir=persist_dir)
        existing_ids = set()

    index = VectorStoreIndex.from_vector_store(store, embed_model=embed_model)
    for db_name, db in tqdm(metadata.items()):
        docs = [
            Document(
                doc_id=db_name + "." + table.name,
                text=_get_document(table, method)[:model_limit],
            )
            for table in db.tables
            if db_name + "." + table.name not in existing_ids
        ]
        if not docs:
            continue
        nodes = dumb_splitter.get_nodes_from_documents(docs)
        assert len(nodes) == len(docs)
        for node in nodes:
            assert node.source_node
            node.id_ = node.source_node.node_id
        index.insert_nodes(nodes)

    token_count_cache = persist_dir + "/token_counts.json"
    if os.path.exists(token_count_cache):
        with open(persist_dir + "/token_counts.json") as f:
            token_counts = json.load(f)
    else:
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
        ids = []
        tables = []
        for db in metadata.values():
            for table in db.tables:
                ids.append(f"{db.name}.{table.name}")
                tables.append(get_table_ddl(table))
        table_token_counts = tokenizer(tables, return_length=True)["length"]
        token_counts: dict[str, int] = dict(zip(ids, table_token_counts))  # type: ignore
        with open(persist_dir + "/token_counts.json", "w") as f:
            json.dump(token_counts, f)

    with shelve.open(persist_dir + "/embedding_cache") as cache:
        query_embed_model = QUERY_EMBED_MODELS.get(model, embed_model)
        questions = load_questions(questions_file)
        async with aclosing(
            run_with_concurrency(
                [
                    partial(
                        _process_question,
                        question,
                        metadata[question.db_id].tables,
                        query_embed_model,
                        store,
                        token_counts,
                        cache,
                        context_limit,
                    )
                    for question in questions
                ],
                concurrency=8,
            )
        ) as results:
            print("db_id\tquestion_id\tquestion\tsql\trecall\tcorrectness\tndcg\tnotes")
            async for _ in tqdm(results):  # type: ignore
                pass


@dataclass
class EvalResult:
    recall: float
    correctness: float
    ndcg: float
    notes: str


async def _process_question(
    question: BIRDQuestion,
    tables: list[Table],
    embed_model: BaseEmbedding,
    store: DuckDBVectorStore,
    token_counts: dict[str, int],
    cache: shelve.Shelf,
    context_limit: int,
) -> None:
    assert question.SQL, "can't evaluate without golden SQL"
    sql_refs = extract_sql_references("", tables, question.SQL, query_runtime_types=False)
    q = question.question.strip()
    if question.evidence:
        q += f" Context: {question.evidence.strip()}"
    q_clean = q.replace("\n", " ")
    question_fields = f"{question.db_id}\t{question.question_id}\t{q_clean}\t{question.SQL}"

    try:
        cache_key = embed_model.model_name + ":" + q
        if not (embedding := cache.get(cache_key)):
            embedding = await embed_model.aget_query_embedding(q)
            cache[cache_key] = embedding
        retrieved = await asyncio.to_thread(
            lambda: store.query(VectorStoreQuery(query_embedding=embedding, similarity_top_k=9999))
        )
        assert retrieved.ids and retrieved.similarities
        token_count = 0
        retrieved_ids = []
        for id, _similarity in zip(retrieved.ids, retrieved.similarities):
            size = token_counts[id]
            if token_count + size > context_limit:
                continue
            token_count += size
            retrieved_ids.append(id)
        relevant_ids = set(f"{question.db_id}.{table}" for table in sql_refs.tables)
        retrieved_id_set = set(retrieved_ids)
        recall = len(relevant_ids & retrieved_id_set) / len(relevant_ids)
        correctness = float(relevant_ids <= retrieved_id_set)

        # Compute NDCG
        def dcg_01(relevance):
            return sum(x / math.log2(i + 2) for i, x in enumerate(relevance))

        ideal_ranking = [1] * len(relevant_ids)
        actual_ranking = [int(id in relevant_ids) for id in retrieved_ids]
        idcg = dcg_01(ideal_ranking)
        dcg = dcg_01(actual_ranking)
        ndcg = dcg / idcg if idcg > 0 else 0

        missing = relevant_ids - retrieved_id_set
        notes = ""
        if missing:
            notes = "Missing: " + ",".join([x.split(".", 1)[1] for x in missing])
        print(f"{question_fields}\t{recall}\t{correctness}\t{ndcg}\t{notes}")
    except Exception as e:
        print(f"{question_fields}\t0\t0\t0\tException: {e}")


if __name__ == "__main__":
    main()
