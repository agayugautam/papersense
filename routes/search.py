from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter()

@router.post("/")
def search_docs(
    query: dict = Body(...),
    db: Session = Depends(get_db)
):
    q = query.get("query", "").lower()

    rows = db.query(Document).all()
    results = [
        {
            "filename": r.filename,
            "document_type": r.document_type
        }
        for r in rows
        if q in (r.content or "").lower()
        or q in r.filename.lower()
    ]

    return {"results": results}
