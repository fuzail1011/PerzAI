from app.parser.pdf_parser import extract_text_from_pdf
from app.parser.docx_parser import extract_text_from_docx
from app.parser.xlsx_parser import extract_text_from_xlsx
from app.parser.txt_parser import extract_text_from_txt


class TextExtractor:
    """
    Dispatches file parsing based on extension.
    """

    def read_file(self, file, filename: str) -> str:
        file_type = filename.split(".")[-1].lower()

        if file_type == "pdf":
            return extract_text_from_pdf(file)
        elif file_type == "docx":
            return extract_text_from_docx(file)
        elif file_type == "xlsx":
            return extract_text_from_xlsx(file)
        elif file_type == "txt":
            return extract_text_from_txt(file)

        return ""
