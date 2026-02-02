from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from services.ai_service import analyze_text, generate_embedding

router = APIRouter()

# ---------- GET ALL DOCUMENTS (RESTORED) ----------

@router.get("")
def get_all_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "document_type": d.document_type,
            "summary": d.summary,
            "size_mb": d.size_mb,
            "blob_path": d.blob_path,
            "created_at": d.created_at,
        }
        for d in docs
    ]

# ---------- UPLOAD DOCUMENT ----------

@router.post("/upload")
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    content = await file.read()
    text = content.decode(errors="ignore")

    analyzed = analyze_text(text)
    embedding = generate_embedding(analyzed["detailed_summary"])

    doc = Document(
        filename=file.filename,
        document_type=analyzed["document_type"],
        parties=",".join(analyzed["parties"]),
        summary=analyzed["summary"],
        detailed_summary=analyzed["detailed_summary"],
        size_mb=len(content) / (1024 * 1024),
        blob_path=file.filename,
        embedding=embedding
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {"id": doc.id}
