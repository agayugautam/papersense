from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from pydantic import BaseModel
import re

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

STOP_WORDS = [
    "show", "me", "give", "find", "list", "get", "all", "please"
]

def normalize_query(q: str):
    q = q.lower()
    tokens = re.findall(r"\w+", q)
    tokens = [t for t in tokens if t not in STOP_WORDS]
    # naive singularization
    normalized = []
    for t in tokens:
        if t.endswith("s") and len(t) > 3:
            t = t[:-1]
        normalized.append(t)
    return " ".join(normalized)

@router.post("/")
def search(payload: SearchRequest, db: Session = Depends(get_db)):
    term = normalize_query(payload.query)

    results = db.query(Document).filter(
        Document.summary.ilike(f"%{term}%") |
        Document.detailed_summary.ilike(f"%{term}%") |
        Document.parties.ilike(f"%{term}%") |
        Document.document_type.ilike(f"%{term}%")
    ).all()

    return results
