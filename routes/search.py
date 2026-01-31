# routes/search.py
from fastapi import APIRouter
from database import SessionLocal
from models import Document
from sqlalchemy import or_

router = APIRouter()

@router.post("/")
def search_documents(payload: dict):
    query = payload.get("query", "").lower()

    db = SessionLocal()

    results = (
        db.query(Document)
        .filter(
            or_(
                Document.filename.ilike(f"%{query}%"),
                Document.extracted_text.ilike(f"%{query}%"),
                Document.document_type.ilike(f"%{query}%")
            )
        )
        .limit(20)
        .all()
    )

    return {
        "results": [
            {
                "filename": d.filename,
                "document_type": d.document_type,
                "parties": [],
                "key_dates": []
            }
            for d in results
        ]
    }
