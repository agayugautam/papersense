from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Document
from services.ai_service import ai_service

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

@router.post("")
async def search_documents(request: SearchRequest, db: Session = Depends(get_db)):
    # 1. Get keywords (e.g., "invoices" -> ["invoices", "invoice"])
    intent = await ai_service.extract_search_intent(request.query)
    keywords = intent.get("keywords", [])

    # 2. Build flexible OR filters
    filters = []
    for word in keywords:
        filters.append(Document.content.ilike(f"%{word}%"))
        filters.append(Document.document_type.ilike(f"%{word}%"))
        filters.append(Document.filename.ilike(f"%{word}%"))

    # 3. Execute
    results = db.query(Document).filter(or_(*filters)).all()
    
    return {"results": results, "count": len(results)}