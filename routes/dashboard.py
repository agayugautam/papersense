from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter()

@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    rows = db.query(Document).all()

    total = len(rows)
    size = sum(r.size_mb or 0 for r in rows)

    recent = [{
        "filename": r.filename,
        "document_type": r.document_type,
        "size_mb": r.size_mb
    } for r in rows[-10:]]

    return {
        "total_documents": total,
        "storage_used_mb": round(size, 2),
        "recent_files": recent
    }
