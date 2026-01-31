from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter()

@router.post("/")
def search(q: dict, db: Session = Depends(get_db)):
    term = q.get("query", "").lower()

    results = db.query(Document).filter(
        Document.summary.ilike(f"%{term}%") |
        Document.detailed_summary.ilike(f"%{term}%") |
        Document.parties.ilike(f"%{term}%")
    ).all()

    return results
