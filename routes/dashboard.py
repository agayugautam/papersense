from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter()

@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    docs = db.query(Document).all()

    total = len(docs)
    size = sum(d.size_mb or 0 for d in docs)

    recent = [
        {
            "filename": d.filename,
            "size_mb": d.size_mb,
            "document_type": d.document_type
        }
        for d in docs[-5:]
    ]

    folders = {}
    for d in docs:
        folders.setdefault(d.document_type or "Other", []).append({
            "filename": d.filename,
            "size_mb": d.size_mb
        })

    return {
        "total_documents": total,
        "storage_used_mb": round(size, 2),
        "recent_files": recent,
        "folders": folders
    }
