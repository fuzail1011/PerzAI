import pdfplumber
from io import BytesIO


async def extract_text_from_pdf(file) -> list[str]:
    """
    Reads text content from a PDF file.
    Returns the text as a single string.
    """
    chunks = []

    # Await the async read
    file_bytes = await file.read()
    pdf_file = BytesIO(file_bytes)

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                chunks.append(page_text.strip())
    return chunks
