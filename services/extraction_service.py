import fitz
import pandas as pd
import docx
from PIL import Image
from io import BytesIO
import csv
import requests
from config import AZURE_FORM_RECOGNIZER_ENDPOINT, AZURE_FORM_RECOGNIZER_KEY

def extract_text(file_bytes: bytes, filename: str) -> str:
    name = filename.lower()
    text = ""

    try:
        # ---------- PDF ----------
        if name.endswith(".pdf"):
            pdf = fitz.open(stream=BytesIO(file_bytes), filetype="pdf")
            for page in pdf:
                text += page.get_text()
            pdf.close()

            # If scanned PDF (no text)
            if len(text.strip()) < 50:
                text = azure_ocr(file_bytes)

        # ---------- Word ----------
        elif name.endswith(".docx"):
            doc = docx.Document(BytesIO(file_bytes))
            for para in doc.paragraphs:
                text += para.text + "\n"

        # ---------- Excel ----------
        elif name.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(file_bytes))
            text = df.to_string()

        # ---------- CSV ----------
        elif name.endswith(".csv"):
            decoded = file_bytes.decode(errors="ignore")
            reader = csv.reader(decoded.splitlines())
            for row in reader:
                text += " ".join(row) + "\n"

        # ---------- Images ----------
        elif name.endswith((".png", ".jpg", ".jpeg", ".webp")):
            text = azure_ocr(file_bytes)

        # ---------- Text / logs ----------
        elif name.endswith((".txt", ".log")):
            text = file_bytes.decode(errors="ignore")

        else:
            text = file_bytes.decode(errors="ignore")

    except Exception as e:
        print("EXTRACTION ERROR:", e)
        return ""

    return text.replace("\x00", " ").strip()


def azure_ocr(file_bytes: bytes) -> str:
    """
    Uses Azure Document Intelligence OCR
    Supports scanned + handwritten
    """
    url = f"{AZURE_FORM_RECOGNIZER_ENDPOINT}/formrecognizer/documentModels/prebuilt-read:analyze?api-version=2023-07-31"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_FORM_RECOGNIZER_KEY,
        "Content-Type": "application/octet-stream"
    }

    resp = requests.post(url, headers=headers, data=file_bytes)
    resp.raise_for_status()

    result = resp.json()
    lines = []

    for page in result.get("analyzeResult", {}).get("pages", []):
        for line in page.get("lines", []):
            lines.append(line["content"])

    return "\n".join(lines)
