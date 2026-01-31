from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter()

@router.post("/")
def search(query: dict, db: Session = Depends(get_db)):
    q = query.get("query", "").lower()

    results = db.query(Document).filter(
        Document.filename.ilike(f"%{q}%")
    ).all()

    return results
