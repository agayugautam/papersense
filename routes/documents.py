# routes/documents.py

import os
import json
from fastapi import APIRouter, UploadFile, File
from services.extraction_service import extract_text
from services.ai_service import analyze_text

router = APIRouter()

UPLOAD_DIR = "uploads"
DATA_FILE = "data/documents.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

def load_docs():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_docs(docs):
    with open(DATA_FILE, "w") as f:
        json.dump(docs, f, indent=2)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_bytes = await file.read()

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    extracted_text = extract_text(file_bytes, file.filename)
    ai_result = analyze_text(extracted_text)

    try:
        ai_data = json.loads(ai_result)
    except:
        ai_data = {
            "document_type": "Unknown",
            "parties": [],
        }

    docs = load_docs()

    doc_record = {
        "filename": file.filename,
        "document_type": ai_data.get("document_type", "Unknown"),
        "size_mb": round(len(file_bytes) / (1024 * 1024), 2)
    }

    docs.append(doc_record)
    save_docs(docs)

    return {"status": "success", "doc": doc_record}
