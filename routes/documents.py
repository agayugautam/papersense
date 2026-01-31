# routes/documents.py

import os
import json
from fastapi import APIRouter, UploadFile, File
from azure.storage.blob import BlobServiceClient
from services.extraction_service import extract_text
from services.ai_service import analyze_text

router = APIRouter()

# Azure config
AZURE_CONN = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "papersense-documents"

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONN)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Metadata store (simple JSON index)
DATA_FILE = "data/documents.json"
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
    # 1. Read file
    file_bytes = await file.read()

    # 2. Upload to Azure Blob
    blob_client = container_client.get_blob_client(file.filename)
    blob_client.upload_blob(file_bytes, overwrite=True)

    # 3. Extract text
    extracted_text = extract_text(file_bytes, file.filename)

    # 4. AI analysis
    ai_result = analyze_text(extracted_text)

    # 5. Safe JSON parsing (never crash)
    try:
        ai_data = json.loads(ai_result)
    except Exception:
        ai_data = {
            "document_type": "Unknown",
            "parties": [],
            "summary": ai_result[:500] if ai_result else ""
        }

    # 6. Save metadata
    docs = load_docs()
    doc_record = {
        "filename": file.filename,
        "document_type": ai_data.get("document_type", "Unknown"),
        "size_mb": round(len(file_bytes) / (1024 * 1024), 2),
        "blob_url": blob_client.url
    }

    docs.append(doc_record)
    save_docs(docs)

    return {
        "status": "success",
        "doc": doc_record
    }
