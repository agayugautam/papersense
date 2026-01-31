# services/extraction_service.py

import io
import pdfplumber
from docx import Document
from PIL import Image

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

from config import (
    AZURE_FORM_RECOGNIZER_ENDPOINT,
    AZURE_FORM_RECOGNIZER_KEY
)


client = DocumentAnalysisClient(
    endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
)


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1]

    try:
        # -------- PDF --------
        if ext == "pdf":
            text = extract_pdf_text(file_bytes)
            if len(text.strip()) > 50:
                return text

            # fallback to Azure OCR for scanned PDF
            return extract_with_azure(file_bytes)

        # -------- Word --------
        if ext == "docx":
            return extract_docx_text(file_bytes)

        # -------- Images --------
        if ext in ["png", "jpg", "jpeg", "webp", "tiff"]:
            return extract_with_azure(file_bytes)

        # -------- Everything else --------
        return extract_with_azure(file_bytes)

    except Exception as e:
        print("Extraction error:", repr(e))
        return ""


# ---------------- PDF ----------------

def extract_pdf_text(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# ---------------- DOCX ----------------

def extract_docx_text(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs])


# ---------------- Azure OCR ----------------

def extract_with_azure(file_bytes: bytes) -> str:
    poller = client.begin_analyze_document(
        "prebuilt-read",
        document=file_bytes
    )
    result = poller.result()

    text = ""
    for page in result.pages:
        for line in page.lines:
            text += line.content + "\n"

    return text
