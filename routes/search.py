from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database import get_db
from models import Document

router = APIRouter()

@router.post("/")
def ai_search(query: str, db: Session = Depends(get_db)):
    q = f"%{query.lower()}%"

    results = db.query(Document).filter(
        or_(
            func.lower(Document.summary).like(q),
            func.lower(Document.detailed_summary).like(q),
            func.lower(Document.keywords).like(q),
            func.lower(Document.parties_involved).like(q),
            func.lower(Document.document_type).like(q),
        )
    ).all()

    return results
