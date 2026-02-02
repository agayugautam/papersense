from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter()

@router.get("/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    all_docs = db.query(Document).all()
    
    # Calculate values to match AppLayout.jsx expectations
    total_docs = len(all_docs)
    total_size = sum(doc.size_mb for doc in all_docs) if all_docs else 0
    recent_docs = all_docs[-10:][::-1] # Last 10 docs, reversed
    
    # This JSON structure is strictly required by your frontend logic
    return {
        "total_documents": total_docs,       # Matches data.total_documents
        "storage_used_mb": total_size,       # Matches data.storage_used_mb
        "recent_files": recent_docs,         # Matches data.recent_files
        "all_documents": all_docs            # Matches data.all_documents
    }