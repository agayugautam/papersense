# src/routes/documents.py
import os
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.extraction_service import extract_text
from services.ai_service import analyze_text

# Azure blob (direct, minimal)
from azure.storage.blob import BlobServiceClient
from config import AZURE_STORAGE_CONNECTION_STRING, AZURE_BLOB_CONTAINER

router = APIRouter()

# Create data dir for JSON index fallback
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "documents.json")
os.makedirs(DATA_DIR, exist_ok=True)

# Try to import DB models — fallback to JSON index
USE_DB = False
try:
    from database import SessionLocal
    from models import Document  # SQLAlchemy model expected
    USE_DB = True
except Exception:
    USE_DB = False


def load_docs_index():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def save_docs_index(docs):
    with open(DATA_FILE, "w") as f:
        json.dump(docs, f, indent=2)


def upload_to_azure_bytes(file_bytes: bytes, filename: str) -> str:
    if not AZURE_STORAGE_CONNECTION_STRING or not AZURE_BLOB_CONTAINER:
        raise RuntimeError("Azure storage configuration missing.")
    service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = service.get_container_client(AZURE_BLOB_CONTAINER)
    # ensure container exists (idempotent)
    try:
        container_client.create_container()
    except Exception:
        pass
    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(file_bytes, overwrite=True)
    return blob_client.url


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # 1. read file
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    # 2. upload to azure (will raise if config missing)
    try:
        blob_url = upload_to_azure_bytes(contents, file.filename)
    except Exception as e:
        print("Azure upload failed:", repr(e))
        raise HTTPException(status_code=500, detail="Failed to upload to storage")

    # 3. extract text (OCR/parse)
    try:
        extracted_text = extract_text(contents, file.filename)
    except Exception as e:
        print("Extraction failed:", repr(e))
        extracted_text = ""

    # 4. classify via AI (robust)
    ai_result = analyze_text(extracted_text or "")

    # Ensure we have a document_type
    doc_type = ai_result.get("document_type") if isinstance(ai_result, dict) else None
    if not doc_type:
        doc_type = "Unknown"

    # 5. persist metadata (DB or JSON index)
    size_mb = round(len(contents) / (1024 * 1024), 2)
    record = {
        "filename": file.filename,
        "document_type": doc_type,
        "size_mb": size_mb,
        "blob_url": blob_url,
        "ai_raw": ai_result.get("raw") if isinstance(ai_result, dict) else None
    }

    if USE_DB:
        try:
            db = SessionLocal()
            doc = Document(
                filename=record["filename"],
                document_type=record["document_type"],
                extracted_text=extracted_text,
                size_mb=record["size_mb"],
                blob_url=record["blob_url"],
            )
            db.add(doc)
            db.commit()
        except Exception as e:
            print("DB save failed:", repr(e))
            # fallback to index
            docs = load_docs_index()
            docs.append(record)
            save_docs_index(docs)
    else:
        docs = load_docs_index()
        docs.append(record)
        save_docs_index(docs)

    # 6. return structured response
    return {"status": "success", "doc": record}

@router.post("/api/documents/reclassify")
def reclassify_all(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    for doc in docs:
        if not doc.document_type or doc.document_type == "Unknown":
            ai = analyze_text(doc.extracted_text or "")
            doc.document_type = ai.get("document_type", "Other")
    db.commit()
    return {"status": "ok", "count": len(docs)}

# Debug endpoint: list docs (works whether using DB or JSON index)
@router.get("/list")
def list_documents():
    if USE_DB:
        db = SessionLocal()
        rows = db.query(Document).all()
        return {"docs": [
            {
                "filename": r.filename,
                "document_type": r.document_type,
                "size_mb": float(r.size_mb or 0),
                "blob_url": getattr(r, "blob_url", None)
            } for r in rows
        ]}
    else:
        docs = load_docs_index()
        return {"docs": docs[::-1]}  # reverse for recent-first
