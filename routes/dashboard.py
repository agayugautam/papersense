from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/metrics")
def dashboard_metrics(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    total = len(docs)
    size_mb = sum(d.size_mb for d in docs)

    recent = docs[-5:]

    folders = {}
    for d in docs:
        folders.setdefault(d.document_type or "Other", []).append(d)

    return {
        "total_documents": total,
        "storage_used_mb": round(size_mb, 2),
        "recent_files": [
            {"filename": d.filename, "size_mb": d.size_mb}
            for d in recent
        ],
        "folders": {
            k: [
                {"filename": f.filename, "size_mb": f.size_mb}
                for f in v
            ]
            for k, v in folders.items()
        }
    }
