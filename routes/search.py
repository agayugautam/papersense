from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from pydantic import BaseModel

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

@router.post("/")
def search(payload: SearchRequest, db: Session = Depends(get_db)):
    term = payload.query.lower()

    results = db.query(Document).filter(
        Document.summary.ilike(f"%{term}%") |
        Document.detailed_summary.ilike(f"%{term}%") |
        Document.parties.ilike(f"%{term}%")
    ).all()

    return results
