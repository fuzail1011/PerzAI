import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.persona import Persona
from app.models.knowledge_base import KnowledgeBase
from app.services.knowledge_service import get_embedding
from app.config import Settings


Settings.validate()


EMBEDDING_DIM = 1536


async def call_llm(context: str, question: str):
    """
    Call the LLM (OpenRouter) and return the response text.
    """

    API_KEY = Settings.OPENROUTER_API_KEY

    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": question},
    ]

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
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]
            return ""


async def retrieve_response(
    db: AsyncSession,
    user_id: int,
    persona_id: int,
    query: str,
    top_k: int = 5,
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

    # 2️⃣ Fetch all chunks for this persona
    result = await db.execute(
        select(KnowledgeBase.chunk_text)
        .where(KnowledgeBase.persona_id == persona_id)
        .where(KnowledgeBase.user_id == user_id)
    )
    chunks = [row[0] for row in result.all()]
    if not chunks:
        context = "No knowledge available yet."
    else:
        # Concatenate all chunks for context
        context = "\n".join(chunks)

    # 3️⃣ Generate embedding for query (optional if semantic search is needed)
    query_embedding = await get_embedding(query)
    if len(query_embedding) != EMBEDDING_DIM:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query embedding dimension mismatch: expected {EMBEDDING_DIM}, got {len(query_embedding)}",
        )

    # 4️⃣ Call LLM
    llm_response = await call_llm(context=context, question=query)

    # 5️⃣ Return response JSON
    return {
        "persona_id": persona.id,
        "persona_name": persona.name,
        "response": llm_response,
    }
