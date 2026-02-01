from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
import re

router = APIRouter()

STOP_WORDS = {
    "show", "me", "documents", "document",
    "related", "to", "find", "get", "please",
    "give", "list", "all"
}

def extract_keywords(text: str):
    words = re.findall(r"\w+", text.lower())
    keywords = [w for w in words if w not in STOP_WORDS]

    # naive singularization (resumes -> resume)
    normalized = []
    for w in keywords:
        if w.endswith("s") and len(w) > 3:
            w = w[:-1]
        normalized.append(w)

    return normalized   # <-- return LIST, not string

@router.post("/")
def search(q: dict, db: Session = Depends(get_db)):
    print("SEARCH HIT:", q)
    raw = q.get("query", "")
    keywords = extract_keywords(raw)

    if not keywords:
        return []

    # Build OR filters dynamically
    filters = []
    for kw in keywords:
        like = f"%{kw}%"
        filters.append(Document.summary.ilike(like))
        filters.append(Document.detailed_summary.ilike(like))
        filters.append(Document.parties.ilike(like))
        filters.append(Document.filename.ilike(like))

    results = db.query(Document).filter(
        *filters
    ).all()

    return {"results": results}
