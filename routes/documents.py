from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from services.extraction_service import extraction_service
from services.blob_service import blob_service

router = APIRouter()

@router.get("")
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.created_at.desc()).all()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        size_mb = round(len(content) / (1024 * 1024), 2)
        
        # Azure Blob Upload
        await blob_service.upload_file(content, file.filename)
        
        # Extract metadata - passing filename for extension check
        result = await extraction_service.ingest_document(content, file.filename)
        analysis = result.get("analysis", {})
        
        new_doc = Document(
            filename=file.filename,
            blob_path=file.filename,
            file_type=file.filename.split(".")[-1],
            size_mb=size_mb,
            content=result.get("content", ""),
            document_type=analysis.get("document_type", "Other"),
            summary=analysis.get("summary", ""),
            detailed_summary=analysis.get("detailed_summary", ""),
            confidence=analysis.get("confidence", 0.0),
            language=analysis.get("language", "en"),
            parties=analysis.get("parties", [])
        )
        
        db.add(new_doc)
        db.commit()
        return {"status": "success"}
        
    except Exception as e:
        db.rollback()
        print(f"UPLOAD CRASH: {e}")
        raise HTTPException(status_code=500, detail=str(e))