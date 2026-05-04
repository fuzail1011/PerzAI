import aiohttp
import time
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.persona import Persona
from app.models.knowledge_base import KnowledgeBase
from app.services.embedding_service import get_embedding
from app.services.reranker import rerank
from app.config import Settings
from loguru import logger

Settings.validate()


EMBEDDING_DIM = Settings.EMBEDDING_DIM


async def call_llm(context: str, question: str):
    """
    Call the LLM (OpenRouter) and return the response text.
    """

    API_KEY = Settings.OPENROUTER_API_KEY

    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": question},
    ]

    t0 = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=Settings.OPENROUTER_ENDPOINT,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": Settings.OPENROUTER_LLM_MODEL,
                "messages": messages,
            },
        ) as resp:
            if resp.status != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"LLM API error: {await resp.text()}",
                )
            result = await resp.json()
            usage = result.get("usage", {})
            logger.info(
                f"llm | endpoint={Settings.OPENROUTER_ENDPOINT} model={Settings.OPENROUTER_LLM_MODEL} "
                f"prompt_tokens={usage.get('prompt_tokens', '?')} "
                f"completion_tokens={usage.get('completion_tokens', '?')} "
                f"duration={time.perf_counter() - t0:.3f}s"
            )
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
            return ""


def _rrf_merge(
    vector_rows: list[tuple],
    fts_rows: list[tuple],
    k: int = 60,
) -> list[str]:
    """Reciprocal Rank Fusion over two ranked lists of (id, chunk_text)."""
    chunk_map: dict[int, str] = {}
    for id_, text in vector_rows + fts_rows:
        chunk_map[id_] = text

    scores: dict[int, float] = {}
    for rank, (id_, _) in enumerate(vector_rows):
        scores[id_] = scores.get(id_, 0.0) + 1.0 / (rank + k)
    for rank, (id_, _) in enumerate(fts_rows):
        scores[id_] = scores.get(id_, 0.0) + 1.0 / (rank + k)

    merged_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [chunk_map[id_] for id_ in merged_ids]


async def retrieve_response(
    db: AsyncSession,
    user_id: int,
    persona_id: int,
    query: str,
    top_k: int = 5,
    source: Optional[str] = None,
    category: Optional[str] = None,
    doc_type: Optional[str] = None,
):
    """
    Retrieve relevant knowledge and generate LLM response for a user and persona.
    Returns only persona info + LLM answer.
    """

    # 1️⃣ Fetch persona
    result = await db.execute(
        select(Persona).where(
            Persona.id == persona_id,
            Persona.user_id == user_id,
        )
    )
    persona = result.scalars().first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found for this user",
        )

    # 2. Embed query
    query_embedding = await get_embedding(query)
    if len(query_embedding) != EMBEDDING_DIM:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query embedding dimension mismatch: expected {EMBEDDING_DIM}, got {len(query_embedding)}",
        )

    # 3. Build base filters (including optional metadata filters)
    base_filters = [
        KnowledgeBase.persona_id == persona_id,
        KnowledgeBase.user_id == user_id,
    ]
    if source:
        base_filters.append(KnowledgeBase._metadata["source"].astext == source)
    if category:
        base_filters.append(KnowledgeBase._metadata["category"].astext == category)
    if doc_type:
        base_filters.append(KnowledgeBase._metadata["doc_type"].astext == doc_type)

    candidate_limit = top_k * 4

    # 4. Dense vector search (cosine similarity)
    vector_result = await db.execute(
        select(KnowledgeBase.id, KnowledgeBase.chunk_text)
        .where(*base_filters)
        .order_by(KnowledgeBase.embedding.cosine_distance(query_embedding))
        .limit(candidate_limit)
    )
    vector_rows = vector_result.all()

    # 5. Sparse keyword search (BM25 via PostgreSQL FTS)
    try:
        fts_result = await db.execute(
            select(KnowledgeBase.id, KnowledgeBase.chunk_text)
            .where(*base_filters)
            .where(
                func.to_tsvector("english", KnowledgeBase.chunk_text).op("@@")(
                    func.plainto_tsquery("english", query)
                )
            )
            .limit(candidate_limit)
        )
        fts_rows = fts_result.all()
    except Exception:
        logger.warning("FTS search failed; falling back to vector-only retrieval")
        fts_rows = []

    # 6. RRF merge — combines both ranked lists
    merged_chunks = _rrf_merge(list(vector_rows), list(fts_rows))
    candidates = merged_chunks[: top_k * 2]
    logger.info(
        f"retrieval | vector={len(vector_rows)} fts={len(fts_rows)} "
        f"merged={len(merged_chunks)} candidates={len(candidates)}"
    )

    # 7. Cross-encoder reranking
    final_chunks = await rerank(query, candidates, top_k)

    # 8. Build context and call LLM
    context = "\n".join(final_chunks) if final_chunks else "No knowledge available yet."
    llm_response = await call_llm(context=context, question=query)

    return {
        "persona_id": persona.id,
        "persona_name": persona.name,
        "response": llm_response,
    }
