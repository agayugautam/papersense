from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from services.ai_service import extract_search_intent
import re

router = APIRouter()

STOP_WORDS = {
    "show", "me", "give", "find", "list", "get",
    "all", "please", "documents", "document", "of", "with",
    "people", "person"
}

# Query synonym normalization
SYNONYM_MAP = {
    "cv": "resume",
    "biodata": "resume",
    "profile": "resume",
    "curriculum vitae": "resume",
    "bill": "invoice",
    "agreement": "contract",
    "purchase order": "po",
}

# AI -> DB document type mapping
AI_DOC_TYPE_MAP = {
    "Resume": "resume",
    "Invoice": "invoice",
    "Receipt": "receipt",
    "Contract": "contract",
    "Report": "report",
    "Purchase Order": "po",
    "PO": "po",
    "Indemnity Letter": "indemnity",
    "Email": "email",
    "Other": None,
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
    
    # Step 1 — normalize synonyms
    normalized = normalize_query(raw)

    print("RAW:", raw)
    print("NORMALIZED:", normalized)

    # Step 2 — AI semantic intent
    try:
        intent = extract_search_intent(normalized)
    except Exception as e:
        print("AI intent failed:", e)
        intent = {
            "document_type": None,
            "min_experience_years": None,
            "keywords": []
        }

    ai_doc_type = intent.get("document_type")
    min_exp = intent.get("min_experience_years")
    keywords = intent.get("keywords", [])

    print("AI TYPE:", ai_doc_type)
    print("AI MIN EXP:", min_exp)
    print("AI KEYWORDS:", keywords)

    # Step 3 — map AI type to DB type
    db_doc_type = None
    if ai_doc_type:
        db_doc_type = AI_DOC_TYPE_MAP.get(ai_doc_type, ai_doc_type.lower())

    query = db.query(Document)

    # Step 4 — filter by document type
    if db_doc_type:
        query = query.filter(
            Document.document_type.ilike(f"%{db_doc_type}%")
        )

    # Step 5 — experience filter (simple semantic)
    if min_exp:
        # crude but effective for v1
        query = query.filter(
            Document.detailed_summary.ilike(f"%{min_exp}%")
        )

    # Step 6 — keyword filters
    for token in keywords:
        token = token.lower()
        if token not in STOP_WORDS:
            query = query.filter(
                Document.detailed_summary.ilike(f"%{token}%")
            )

    results = query.all()
    serialized = [serialize_document(d) for d in results]

    return {"results": serialized}
