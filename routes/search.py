from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
import re
from services.ai_service import extract_search_intent

router = APIRouter()

DOC_TYPES = ["resume", "invoice", "receipt", "contract", "report", "po"]

STOP_WORDS = {
    "show", "me", "give", "find", "list", "get",
    "all", "please", "documents", "document", "of", "with"
}

# Semantic normalization layer
SYNONYM_MAP = {
    "cv": "resume",
    "biodata": "resume",
    "profile": "resume",
    "curriculum vitae": "resume",
    "bill": "invoice",
    "agreement": "contract",
    "purchase order": "po"
}

def normalize_query(query: str):
    q = query.lower()
    for k, v in SYNONYM_MAP.items():
        if k in q:
            q = q.replace(k, v)
    return q


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


@router.post("")
def search(q: dict, db: Session = Depends(get_db)):
    raw = q.get("query", "")
    
    # Step 1: normalize (CV -> Resume)
    normalized = normalize_query(raw)

    print("RAW:", raw)
    print("NORMALIZED:", normalized)

    # Step 2: AI intent extraction
    try:
        intent = extract_search_intent(normalized)
    except Exception as e:
        print("AI intent failed, fallback to raw:", e)
        intent = {
            "document_type": None,
            "keywords": []
        }

    doc_type = intent.get("document_type")
    keywords = intent.get("keywords", [])

    print("AI TYPE:", doc_type)
    print("AI KEYWORDS:", keywords)

    query = db.query(Document)

    # Step 3: semantic document type filter
    if doc_type:
        query = query.filter(
            Document.document_type.ilike(f"%{doc_type}%")
        )

    # Step 4: semantic keyword filter
    for token in keywords:
        if token.lower() not in STOP_WORDS:
            query = query.filter(
                Document.detailed_summary.ilike(f"%{token}%")
            )

    results = query.all()
    serialized = [serialize_document(d) for d in results]

    return {"results": serialized}
