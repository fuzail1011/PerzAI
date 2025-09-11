from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PersonaCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PersonaDelete(BaseModel):
    id: int


class PersonaOut(BaseModel):
    id: int
    name: str
    description: str | None
    system_prompt: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemPromptUpdate(BaseModel):
    persona_id: int
    system_prompt: str
