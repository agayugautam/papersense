# backend/routes/search.py

import json
import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document, DocumentChunk
from services.ai_service import embed_text

router = APIRouter()


# ===========================
# Utility: Cosine Similarity
# ===========================

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ===========================
# API
# ===========================

@router.post("")
def search(q: dict, db: Session = Depends(get_db)):
    query_text = q.get("query", "").strip()
    if not query_text:
        return {"results": []}

    # 1. Embed query
    query_vector = embed_text(query_text)

    # 2. Load all chunks
    chunks = db.query(DocumentChunk).all()

    if not chunks:
        return {"results": []}

    # 3. Compute similarities
    scored = []
    for chunk in chunks:
        chunk_vector = json.loads(chunk.embedding)
        score = cosine_similarity(query_vector, chunk_vector)
        scored.append((chunk.document_id, score))

    # 4. Aggregate best score per document
    doc_scores = {}
    for doc_id, score in scored:
        if doc_id not in doc_scores:
            doc_scores[doc_id] = score
        else:
            doc_scores[doc_id] = max(doc_scores[doc_id], score)

    # 5. Sort documents by relevance
    ranked_doc_ids = sorted(
        doc_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    # 6. Fetch documents
    results = []
    for doc_id, score in ranked_doc_ids:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            results.append({
                "id": doc.id,
                "filename": doc.filename,
                "document_type": doc.document_type,
                "summary": doc.summary,
                "detailed_summary": doc.detailed_summary,
                "blob_url": doc.blob_url,
                "score": float(score)
            })

    return {"results": results}
