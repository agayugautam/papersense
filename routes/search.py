from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter()

class SearchRequest(BaseModel):
    query: str # Matches body: JSON.stringify({ query }) from AISearch.jsx

@router.post("")
async def run_ai_search(request: SearchRequest, db: Session = Depends(get_db)):
    raw_q = request.query.strip().lower()
    
    # Handle simple pluralization (e.g., invoices -> invoice)
    stemmed_q = raw_q[:-1] if raw_q.endswith('s') else raw_q
    
    from sqlalchemy import or_
    
    # Search for original query OR stemmed version in Content, Type, or Filename
    results = db.query(Document).filter(
        or_(
            Document.content.ilike(f"%{raw_q}%"),
            Document.content.ilike(f"%{stemmed_q}%"),
            Document.document_type.ilike(f"%{raw_q}%"),
            Document.document_type.ilike(f"%{stemmed_q}%"),
            Document.filename.ilike(f"%{raw_q}%")
        )
    ).all()
    
    return {"results": results, "count": len(results)}