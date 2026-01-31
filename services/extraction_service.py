# services/extraction_service.py

import os
import fitz  # PyMuPDF
import docx
import pandas as pd
from PIL import Image
import pytesseract
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import (
    AZURE_FORM_RECOGNIZER_ENDPOINT,
    AZURE_FORM_RECOGNIZER_KEY
)

# ----------------------------
# Main entry point
# ----------------------------
def extract_text(file_path: str, filename: str) -> str:
    ext = filename.lower().split(".")[-1]

    text = ""

    try:
        if ext == "pdf":
            text = extract_text_from_pdf(file_path)

            # Fallback to OCR if empty
            if len(text.strip()) < 50:
                print("PDF looks scanned. Using Azure OCR...")
                text = extract_text_with_azure_ocr(file_path)

        elif ext in ["docx"]:
            text = extract_text_from_docx(file_path)

        elif ext in ["xlsx", "xls", "csv"]:
            text = extract_text_from_excel(file_path)

        elif ext in ["png", "jpg", "jpeg", "webp"]:
            text = extract_text_from_image(file_path)

        else:
            print("Unknown file type, using OCR fallback...")
            text = extract_text_with_azure_ocr(file_path)

    except Exception as e:
        print("Extraction error:", repr(e))
        text = ""

    print("EXTRACTED TEXT LENGTH:", len(text))
    print("SAMPLE TEXT:", text[:300])

    return text.strip()


# ----------------------------
# PDF (digital)
# ----------------------------
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    doc = fitz.open(file_path)

    for page in doc:
        text += page.get_text()

    return text


# ----------------------------
# DOCX
# ----------------------------
def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


# ----------------------------
# Excel / CSV
# ----------------------------
def extract_text_from_excel(file_path: str) -> str:
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    return df.to_string()


# ----------------------------
# Image (local OCR - fallback)
# ----------------------------
def extract_text_from_image(file_path: str) -> str:
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)


# ----------------------------
# Azure OCR (enterprise grade)
# ----------------------------
def extract_text_with_azure_ocr(file_path: str) -> str:
    if not AZURE_FORM_RECOGNIZER_ENDPOINT or not AZURE_FORM_RECOGNIZER_KEY:
        print("Azure OCR not configured.")
        return ""

    client = DocumentAnalysisClient(
        endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
        credential=AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
    )

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-read", f)
        result = poller.result()

    text = ""
    for page in result.pages:
        for line in page.lines:
            text += line.content + "\n"

    return text
