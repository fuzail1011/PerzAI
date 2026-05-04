import asyncio
from functools import lru_cache
from loguru import logger

_RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def _load_cross_encoder():
    from sentence_transformers import CrossEncoder
    logger.info(f"loading cross-encoder model: {_RERANK_MODEL}")
    return CrossEncoder(_RERANK_MODEL)


async def rerank(query: str, chunks: list[str], top_k: int) -> list[str]:
    if not chunks:
        return []
    if len(chunks) <= top_k:
        return chunks

    model = _load_cross_encoder()
    pairs = [[query, chunk] for chunk in chunks]
    loop = asyncio.get_event_loop()
    scores = await loop.run_in_executor(None, lambda: model.predict(pairs).tolist())

    ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    logger.info(f"reranker | candidates={len(chunks)} top_k={top_k} top_score={ranked[0][0]:.4f}")
    return [chunk for _, chunk in ranked[:top_k]]
