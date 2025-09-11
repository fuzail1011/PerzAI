from pydantic import BaseModel
from datetime import datetime


class PersonaCreate(BaseModel):
    name: str
    description: str | None = None


class PersonaDelete(BaseModel):
    id: int


class PersonaOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
