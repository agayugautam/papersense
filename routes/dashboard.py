from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import Document

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Returns metrics for dashboard:
    - total_documents
    - storage_used_mb
    - recent_files (last 5 uploads)
    """

    total_documents = db.query(Document).count()

    storage_used_mb = (
        db.query(func.sum(Document.size_mb))
        .scalar()
    ) or 0

    recent_files = (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_documents": total_documents,
        "storage_used_mb": round(storage_used_mb, 2),
        "recent_files": recent_files
    }
