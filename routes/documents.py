# routes/documents.py

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from models import Document
from services.ai_service import analyze_text
from services.extraction_service import extract_text
from services.azure_blob_service import upload_to_azure

router = APIRouter(prefix="/api/documents", tags=["documents"])


# =========================
# Upload document
# =========================
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Read bytes
    file_bytes = await file.read()

    # Upload to Azure
    blob_url = upload_to_azure(file_bytes, file.filename)

    # Extract text
    extracted_text = extract_text(file_bytes, file.filename)

    # AI classify
    ai_result = analyze_text(extracted_text)
    doc_type = ai_result.get("document_type", "Other")

    # Save to DB
    doc = Document(
        filename=file.filename,
        document_type=doc_type,
        blob_url=blob_url,
        size_mb=len(file_bytes) / (1024 * 1024)
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type
    }


# =========================
# Get all documents
# =========================
@router.get("/")
def get_all_documents(db: Session = Depends(get_db)):
    rows = db.query(Document).order_by(Document.id.desc()).all()
    return rows


# =========================
# Reclassify everything
# =========================
@router.post("/reclassify")
def reclassify_all(db: Session = Depends(get_db)):
    rows = db.query(Document).all()

    for doc in rows:
        text = doc.filename  # fallback
        ai = analyze_text(text)
        doc.document_type = ai.get("document_type", "Other")

    db.commit()
    return {"reclassified": len(rows)}
