from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from services.blob_service import upload_to_azure
from services.extraction_service import extract_text
from services.ai_service import analyze_document

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    data = await file.read()
    size_mb = len(data) / (1024 * 1024)

    # 1. Upload to Azure FIRST
    try:
        blob_path = upload_to_azure(file.filename, data)
    except Exception as e:
        print("AZURE FAILED:", e)
        raise HTTPException(500, "Azure upload failed")

    # 2. Extract text FROM REAL FILE
    text = extract_text(data, file.filename)

    # 3. AI analysis
    ai = analyze_document(text)

    # 4. Insert into DB ONLY AFTER Azure success
    doc = Document(
        filename=file.filename,
        document_type=ai.get("document_type", "Other"),
        parties=ai.get("parties", ""),
        summary=ai.get("summary", ""),
        detailed_summary=ai.get("detailed_summary", ""),
        size_mb=size_mb,
        blob_path=blob_path
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc
