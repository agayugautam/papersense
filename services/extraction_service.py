# services/extraction_service.py
import fitz  # PyMuPDF
import pandas as pd
from docx import Document
import io

def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.split(".")[-1].lower()

    if ext == "pdf":
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join([page.get_text() for page in doc])

    elif ext in ["csv"]:
        df = pd.read_csv(io.BytesIO(file_bytes))
        return df.to_string()

    elif ext in ["xlsx", "xls"]:
        df = pd.read_excel(io.BytesIO(file_bytes))
        return df.to_string()

    elif ext == "docx":
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])

    else:
        return ""
