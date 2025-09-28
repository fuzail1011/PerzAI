import pdfplumber


def extract_text_from_pdf(file) -> str:
    """
    Reads text content from a PDF file.
    Returns the text as a single string.
    """
    text_content = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text.strip())
    return " ".join(text_content)
