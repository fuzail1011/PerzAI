from io import BytesIO
import openpyxl
import re


async def extract_text_from_xlsx(file) -> list[str]:
    """
    Reads text content from an XLSX file (all sheets).
    Returns the text as a single string.
    """
    file_bytes = await file.read()
    workbook = openpyxl.load_workbook(BytesIO(file_bytes), data_only=True)
    chunks = []

    for sheet in workbook.sheetnames:
        worksheet = workbook[sheet]
        for row in worksheet.iter_rows(values_only=True):
            row_text = " ".join([str(cell) for cell in row if cell is not None]).strip()
            row_text = re.sub(r"\s+", " ", row_text)
            if row_text:
                chunks.append(row_text)

    return chunks
