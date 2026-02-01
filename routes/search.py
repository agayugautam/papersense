from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from pydantic import BaseModel
import re
from services.ai_service import extract_search_intent

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
def search(q: dict, db: Session = Depends(get_db)):
    query = q.get("query", "")

    intent = extract_search_intent(query)

    doc_type = intent.get("document_type")
    min_exp = intent.get("min_experience_years")
    keywords = intent.get("keywords", [])

    qset = db.query(Document)

    # 1. Filter by document type
    if doc_type:
        qset = qset.filter(Document.document_type.ilike(f"%{doc_type}%"))

    # 2. Keyword semantic filter
    for kw in keywords:
        qset = qset.filter(
            Document.detailed_summary.ilike(f"%{kw}%")
        )

    # 3. Experience heuristic
    if min_exp:
        qset = qset.filter(
            Document.detailed_summary.ilike("%year%")
        )

    results = qset.all()
    return results
