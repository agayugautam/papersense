from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter()

@router.get("/metrics")
def dashboard_metrics(db: Session = Depends(get_db)):
    rows = db.query(Document).all()

    total = len(rows)
    storage = sum([r.size_mb for r in rows])

    recent = rows[-10:]

    return {
        "total_documents": total,
        "storage_used_mb": round(storage, 2),
        "recent_files": [
            {
                "filename": r.filename,
                "document_type": r.document_type,
                "size_mb": r.size_mb
            }
            for r in recent
        ]
    }
