import asyncio
import time
import aiohttp
from functools import lru_cache
from app.config import Settings
from loguru import logger


@lru_cache(maxsize=1)
def _load_local_model():
    """Lazy singleton — model is downloaded and loaded once on first call."""
    from sentence_transformers import SentenceTransformer
    logger.info(f"loading local embedding model: {Settings.LOCAL_EMBEDDING_MODEL}")
    return SentenceTransformer(Settings.LOCAL_EMBEDDING_MODEL)


def get_embedding_model_name() -> str:
    if Settings.EMBEDDING_TYPE == "local":
        return Settings.LOCAL_EMBEDDING_MODEL
    return Settings.AZURE_DEPLOYMENT


async def get_embedding(text: str) -> list:
    if Settings.EMBEDDING_TYPE == "local":
        return await _embed_local(text)
    return await _embed_azure(text)


async def _embed_azure(text: str) -> list:
    url = (
        f"{Settings.AZURE_ENDPOINT}/openai/deployments/"
        f"{Settings.AZURE_DEPLOYMENT}/embeddings?"
        f"api-version={Settings.AZURE_API_VERSION}"
    )
    headers = {"Content-Type": "application/json", "api-key": Settings.AZURE_API_KEY}
    payload = {"input": text}

    t0 = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
            data = await resp.json()
            logger.info(
                f"embedding | provider=azure model={Settings.AZURE_DEPLOYMENT} "
                f"duration={time.perf_counter() - t0:.3f}s"
            )
            return data["data"][0]["embedding"]


async def _embed_local(text: str) -> list:
    model = _load_local_model()
    t0 = time.perf_counter()
    loop = asyncio.get_event_loop()
    # SentenceTransformer.encode() is synchronous — offload to thread pool
    embedding = await loop.run_in_executor(None, lambda: model.encode(text).tolist())
    logger.info(
        f"embedding | provider=local model={Settings.LOCAL_EMBEDDING_MODEL} "
        f"duration={time.perf_counter() - t0:.3f}s"
    )
    return embedding
