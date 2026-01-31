from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from services.ai_service import analyze_text

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content_bytes = await file.read()
    text = content_bytes.decode(errors="ignore")

    ai = analyze_text(text)
    doc_type = ai.get("document_type", "Other")

    size_mb = len(content_bytes) / (1024 * 1024)

    doc = Document(
        filename=file.filename,
        document_type=doc_type,
        size_mb=size_mb,
        content=text[:5000]
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type
    }


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    rows = db.query(Document).all()
    return rows
