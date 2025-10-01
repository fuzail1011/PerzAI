from typing import List
from app.parser.main_extractor import TextExtractor


async def chunk_document_by_page(file) -> List[str]:
    """
    Returns a list of chunks, one per page/paragraph/sheet depending on file type.
    """
    extractor = TextExtractor()
    return await extractor.read_file(
        file,
        file.filename,
    )
