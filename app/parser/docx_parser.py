import docx


def extract_text_from_docx(file) -> list[str]:
    """
    Reads text content from a DOCX file (paragraphs + tables).
    Returns the text as a single string.
    """
    doc = docx.Document(file)
    chunks = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            chunks.append(paragraph.text.strip())

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                cell_text = cell.text.strip()
                if cell_text:
                    chunks.append(cell_text)

    return chunks
