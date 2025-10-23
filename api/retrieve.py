from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.retrieval_service import retrieve_response
from pydantic import BaseModel
from typing import Optional
from loguru import logger

router = APIRouter(prefix="/retrieve", tags=["Retrieval"])


class RetrievalRequest(BaseModel):
    query: str
    persona_id: int
    top_k: Optional[int] = 5


@router.post("/")
async def retrieve_endpoint(
    payload: RetrievalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Perform similarity-based semantic retrieval and return an LLM-generated answer.
    user_id is taken from JWT (current_user).
    """
    try:
        response = await retrieve_response(
            db=db,
            user_id=int(current_user),
            persona_id=payload.persona_id,
            query=payload.query,
            top_k=payload.top_k or 5,
        )
        return response
    except Exception as e:
        logger.exception("Error in retrieval endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
