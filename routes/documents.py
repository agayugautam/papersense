from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
import json

from database import get_db
from models import Document
from services.ai_service import analyze_text
from services.extraction_service import extract_text

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    content = await file.read()
    text = extract_text(content, file.filename)

    ai = analyze_text(text)

    doc = Document(
        filename=file.filename,
        document_type=ai["document_type"],
        size_mb=len(content) / (1024 * 1024),
        parties_involved=json.dumps(ai["parties_involved"]),
        summary=ai["summary"],
        detailed_summary=ai["detailed_summary"],
        keywords=json.dumps(ai["keywords"]),
        content=text
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type
    }
