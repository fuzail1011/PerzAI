import aiohttp
from datetime import datetime
import uuid
from app.models.knowledge_base import KnowledgeBase
from app.chunking.chunk import chunk_document_by_page
import mimetypes
from app.config import Settings

Settings.validate()


async def get_embedding(text: str):
    url = (
        f"{Settings.AZURE_ENDPOINT}/openai/deployments/"
        f"{Settings.AZURE_DEPLOYMENT}/embeddings?"
        f"api-version={Settings.AZURE_API_VERSION}"
    )
    headers = {
        "Content-Type": "application/json",
        "api-key": Settings.AZURE_API_KEY,
    }
    payload = {"input": text}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers=headers,
            json=payload,
        ) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
            data = await resp.json()
            return data["data"][0]["embedding"]


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
