def extract_text_from_txt(file) -> list[str]:
    """
    Reads text content from a TXT file.
    Returns the text as a single string.
    """
    file.file.seek(0)
    lines = file.file.read().decode("utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]
