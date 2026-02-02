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
    q = request.query.lower()
    
    # Simple semantic-style search across filename, content, and type
    results = db.query(Document).filter(
        (Document.filename.ilike(f"%{q}%")) | 
        (Document.content.ilike(f"%{q}%")) |
        (Document.document_type.ilike(f"%{q}%"))
    ).all()
    
    return {"results": results}