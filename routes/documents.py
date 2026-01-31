from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Document
from services.blob_service import upload_to_azure
from services.extraction_service import extract_text_from_pdf
from services.ai_service import analyze_text

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    url = upload_to_azure(contents, file.filename)

    text = ""
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(contents)

    ai = analyze_text(text)
    doc_type = ai.get("document_type", "Other")

    size_mb = len(contents) / (1024 * 1024)

    doc = Document(
        filename=file.filename,
        url=url,
        document_type=doc_type,
        size_mb=size_mb
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    rows = db.query(Document).order_by(Document.id.desc()).all()
    return rows
