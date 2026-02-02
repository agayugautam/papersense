# backend/routes/search.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from services.ai_service import generate_embedding
from sqlalchemy import text

router = APIRouter()

def serialize_document(doc: Document):
    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_type": doc.document_type,
        "summary": doc.summary,
        "size_mb": doc.size_mb,
        "blob_path": doc.blob_path
    }

@router.post("")
def search(q: dict, db: Session = Depends(get_db)):
    query_text = q.get("query", "").strip()
    if not query_text:
        return {"results": []}

    query_embedding = generate_embedding(query_text)

    sql = text("""
        SELECT *
        FROM documents
        WHERE embedding IS NOT NULL
        ORDER BY embedding <-> :embedding
        LIMIT 10;
    """)

    results = db.execute(
        sql,
        {"embedding": query_embedding}
    ).fetchall()

    docs = [serialize_document(Document(**row._mapping)) for row in results]
    return {"results": docs}
