from pydantic import BaseModel


class RetrieveRequest(BaseModel):
    query: str
    persona_id: int


class RetrieveResponse(BaseModel):
    persona_id: int
    persona_name: str
    llm_response: str
