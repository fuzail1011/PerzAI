from typing import List
from app.parser.main_extractor import TextExtractor
from app.chunking.semantic_chunker import split_text

_SEMANTIC_EXTS = {".pdf", ".docx", ".txt"}


async def chunk_document_by_page(file) -> List[str]:
    extractor = TextExtractor()
    raw_sections = await extractor.read_file(file, file.filename)

    ext = ""
    if "." in file.filename:
        ext = "." + file.filename.rsplit(".", 1)[-1].lower()

    if ext in _SEMANTIC_EXTS:
        full_text = "\n\n".join(s for s in raw_sections if s and s.strip())
        return split_text(full_text)

    return [s for s in raw_sections if s and s.strip()]
