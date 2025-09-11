from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.persona import Persona
from app.schemas.persona import PersonaCreate, PersonaDelete, SystemPromptUpdate


async def create_persona(
    db: AsyncSession,
    user_id: int,
    persona_data: PersonaCreate,
):
    # Check for duplicate persona name for the same user
    result = await db.execute(
        select(Persona).where(
            Persona.user_id == user_id,
            Persona.name == persona_data.name,
        )
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Persona with this name already exists for this user",
        )

    persona = Persona(
        user_id=user_id,
        name=persona_data.name,
        description=persona_data.description,
    )
    db.add(persona)

    try:
        await db.commit()
        await db.refresh(persona)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create persona due to database constraint",
        )

    return persona


async def get_personas_for_user(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Persona).where(Persona.user_id == user_id).order_by(Persona.created_at.desc())
    )
    return result.scalars().all()


async def delete_persona(
    db: AsyncSession,
    user_id: int,
    payload: PersonaDelete,
):
    result = await db.execute(
        select(Persona).where(
            Persona.id == payload.id,
            Persona.user_id == user_id,
        )
    )
    persona = result.scalars().first()

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found or not owned by this user",
        )

    await db.delete(persona)
    await db.commit()

    return {
        "status": "success",
        "message": f"Persona '{persona.name}' deleted",
    }


async def update_system_prompt(
    db: AsyncSession,
    persona_id: int,
    user_id: int,
    system_prompt: str,
):
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
            detail="Persona not found",
        )

    persona.system_prompt = system_prompt
    await db.commit()
    await db.refresh(persona)
    return persona
