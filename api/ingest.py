from fastapi import APIRouter, Depends, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.knowledge_service import ingest_document
from app.parser.main_extractor import TextExtractor

router = APIRouter(prefix="/ingest", tags=["ingest"])
extractor = TextExtractor()


@router.post("/")
async def upload_document(
    file: UploadFile,
    persona_id: int = Form(...),
    source: str = Form(...),
    category: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Ingests a file into the knowledge base for the logged-in user and specified persona.
    """
    user_id = int(current_user)
    return await ingest_document(
        db,
        file,
        user_id,
        persona_id,
        source,
        category,
    )
