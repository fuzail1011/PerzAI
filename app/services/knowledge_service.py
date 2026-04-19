from datetime import datetime
import uuid
from app.models.knowledge_base import KnowledgeBase
from app.chunking.chunk import chunk_document_by_page
import mimetypes
from app.config import Settings
from app.services.embedding_service import get_embedding
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.persona import Persona
from loguru import logger

Settings.validate()


async def ingest_document(
    db,
    file,
    user_id: int,
    persona_id: int,
    source: str,
    category: str,
):
    doc_id = str(uuid.uuid4())
    file.file.seek(0)

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(file.filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Page-based chunks
    pages = await chunk_document_by_page(file)
    if not pages:
        return {
            "status": "error",
            "message": "No text could be extracted from the file",
        }

    for page_number, page_text in enumerate(pages, start=1):
        embedding = await get_embedding(page_text)
        metadata = {
            "doc_id": doc_id,
            "document_name": file.filename,
            "user_id": user_id,
            "persona_id": persona_id,
            "page_number": page_number,
            "doc_type": mime_type,  # now stores MIME type
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "category": category,
        }

        kb_entry = KnowledgeBase(
            doc_id=doc_id,
            document_name=file.filename,
            user_id=user_id,
            persona_id=persona_id,
            chunk_text=page_text,
            embedding=embedding,
            _metadata=metadata,
        )
        db.add(kb_entry)

    await db.commit()

    return {
        "status": "success",
        "doc_id": doc_id,
        "document_name": file.filename,
        "user_id": user_id,
        "persona_id": persona_id,
        "total_chunks": len(pages),
        "metadata": {
            "doc_id": doc_id,
            "document_name": file.filename,
            "user_id": user_id,
            "persona_id": persona_id,
            "doc_type": mime_type,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "category": category,
        },
        "message": "Document ingested successfully",
    }


async def get_documents_by_user(
    db: AsyncSession,
    user_id: int,
):
    """
    Returns all documents grouped by persona for a given user_id
    """
    stmt = (
        select(
            KnowledgeBase.persona_id,
            Persona.name.label("persona_name"),
            KnowledgeBase.document_name,
        )
        .join(Persona, Persona.id == KnowledgeBase.persona_id)
        .where(KnowledgeBase.user_id == user_id)
        .distinct()
    )

    result = await db.execute(stmt)
    rows = result.all()

    personas = {}
    for persona_id, persona_name, document_name in rows:
        if persona_id not in personas:
            personas[persona_id] = {
                "persona_id": persona_id,
                "persona_name": persona_name,
                "kb_documents": [],
            }
        personas[persona_id]["kb_documents"].append(document_name)

    return {
        "status": "success",
        "personas": list(personas.values()),
    }
