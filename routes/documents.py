# backend/routes/documents.py

from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from services.extraction_service import ingest_document

router = APIRouter()


# ===========================
# GET ALL DOCUMENTS
# ===========================

@router.get("")
def get_all_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "document_type": d.document_type,
            "summary": d.summary,
            "detailed_summary": d.detailed_summary,
            "blob_url": d.blob_url,
            "created_at": d.created_at,
        }
        for d in docs
    ]


# ===========================
# UPLOAD DOCUMENT
# ===========================

@router.post("/upload")
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    file_bytes = await file.read()

    document_id = ingest_document(
        file_bytes=file_bytes,
        filename=file.filename,
        db=db
    )

    return {
        "id": document_id,
        "filename": file.filename,
        "status": "ingested"
    }
