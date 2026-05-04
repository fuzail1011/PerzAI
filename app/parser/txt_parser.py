async def extract_text_from_txt(file) -> list[str]:
    """
    Reads text content from a TXT file.
    Returns the text as a single string.
    """
    file_bytes = await file.read()
    lines = file_bytes.decode("utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]
