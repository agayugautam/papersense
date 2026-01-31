from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter()

@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return {
        "total_documents": len(docs),
        "storage_used_mb": sum(d.size_mb for d in docs),
        "recent_files": docs[-10:]
    }
