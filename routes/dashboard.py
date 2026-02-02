from fastapi import APIRouter
from database import SessionLocal
from models import Document

router = APIRouter()


@router.get("/api/dashboard/metrics")
def metrics():
    db = SessionLocal()
    docs = db.query(Document).all()

    total = len(docs)
    storage_used_mb = sum(d.size_mb or 0 for d in docs)

    folders = {}
    for d in docs:
        t = d.document_type or "Other"
        folders[t] = folders.get(t, 0) + 1

    recent = sorted(
        docs,
        key=lambda d: d.created_at,
        reverse=True
    )[:10]

    return {
        "total": total,
        "size_mb": storage_used_mb,
        "folders": folders,
        "recent": [
            {
                "id": d.id,
                "filename": d.filename,
                "document_type": d.document_type,
                "size_mb": d.size_mb,
                "created_at": d.created_at,
            }
            for d in recent
        ],
        "allDocuments": [
            {
                "id": d.id,
                "filename": d.filename,
                "document_type": d.document_type,
                "created_at": d.created_at,
            }
            for d in docs
        ]
    }
