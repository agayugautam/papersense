from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Document
from services.blob_service import upload_file
from services.extraction_service import extract_text
from services.ai_service import classify_document
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)

    blob_path = upload_file(file_bytes, file.filename)

    extracted_text = extract_text(file_bytes, file.filename)

    ai_result = classify_document(extracted_text)
    ai_data = json.loads(ai_result)

    doc = Document(
        filename=file.filename,
        document_type=ai_data["document_type"],
        category=ai_data["category"],
        summary=ai_data["summary"],
        detailed_summary=ai_data["detailed_summary"],
        size_mb=size_mb,
        blob_path=blob_path
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {"id": doc.id, "status": "uploaded"}
