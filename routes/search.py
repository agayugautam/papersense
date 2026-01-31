from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter(prefix="/api/search", tags=["search"])

@router.post("/")
def search_docs(payload: dict, db: Session = Depends(get_db)):
    q = payload.get("query", "").lower()

    results = db.query(Document).filter(
        Document.filename.ilike(f"%{q}%")
    ).all()

    return results
