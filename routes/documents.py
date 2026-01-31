from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from services.blob_service import upload_to_azure
from services.extraction_service import extract_text_from_pdf
from services.ai_service import analyze_text

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    bytes_data = await file.read()
    blob_url = upload_to_azure(bytes_data, file.filename)

    extracted_text = ""
    if file.filename.lower().endswith(".pdf"):
        extracted_text = extract_text_from_pdf(bytes_data)

    doc_type = analyze_text(extracted_text)

    doc = Document(
        filename=file.filename,
        blob_url=blob_url,
        document_type=doc_type,
        size_mb=len(bytes_data) / (1024 * 1024)
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {"status": "ok", "document_type": doc_type}

@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()
