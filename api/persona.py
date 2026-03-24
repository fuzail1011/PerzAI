from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.persona import PersonaCreate, PersonaOut, PersonaDelete, SystemPromptUpdate
from app.services.persona_service import (
    create_persona,
    get_personas_for_user,
    delete_persona,
    update_system_prompt,
)

router = APIRouter(prefix="/personas", tags=["personas"])


@router.post("/create", response_model=PersonaOut)
async def create_new_persona(
    persona: PersonaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    return await create_persona(
        db,
        int(current_user),
        persona,
    )


@router.get("/my", response_model=List[PersonaOut])
async def list_user_personas(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    return await get_personas_for_user(db, int(current_user))


@router.delete("/delete")
async def delete_user_persona(
    payload: PersonaDelete,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    return await delete_persona(
        db,
        int(current_user),
        payload,
    )


@router.put("/system-prompt")
async def set_system_prompt(
    payload: SystemPromptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),  # JWT returns user_id as string
):
    updated_persona = await update_system_prompt(
        db,
        int(current_user),
        payload.persona_id,
        payload.system_prompt,
    )

    return {
        "status": "success",
        "message": "System prompt updated successfully",
        "persona": updated_persona,
    }
