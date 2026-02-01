from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
import re

router = APIRouter()

DOC_TYPES = ["resume", "invoice", "receipt", "contract", "report"]

STOP_WORDS = {
    "show", "me", "give", "find", "list", "get",
    "all", "please", "documents", "document", "of", "with"
}

def extract_intent(query: str):
    q = query.lower()

    main_type = None
    for t in DOC_TYPES:
        if t in q:
            main_type = t
            q = q.replace(t, "")
            break

    tokens = re.findall(r"\w+", q)
    filters = [t for t in tokens if t not in STOP_WORDS]

    return main_type, filters


def serialize_document(doc: Document):
    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type,
        "parties": doc.parties,
        "summary": doc.summary,
        "detailed_summary": doc.detailed_summary,
        "size_mb": doc.size_mb,
        "blob_path": doc.blob_path
    }


@router.post("/")
def search(q: dict, db: Session = Depends(get_db)):
    raw = q.get("query", "")
    main_type, filters = extract_intent(raw)

    print("RAW:", raw)
    print("TYPE:", main_type)
    print("FILTER TOKENS:", filters)

    query = db.query(Document)

    # Step 1: filter by document type
    if main_type:
        query = query.filter(
            Document.document_type.ilike(f"%{main_type}%")
        )

    # Step 2: apply detailed filters (token-wise)
    for token in filters:
        query = query.filter(
            Document.detailed_summary.ilike(f"%{token}%")
        )

    results = query.all()

    # CRITICAL FIX: serialize ORM objects
    serialized = [serialize_document(d) for d in results]

    return {"results": serialized}
