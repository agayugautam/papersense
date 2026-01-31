# routes/documents.py

import os
import json
from fastapi import APIRouter, UploadFile, File
from services.extraction_service import extract_text
from services.ai_service import analyze_text

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Read file
    file_bytes = await file.read()

    # Save to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Extract text
    extracted_text = extract_text(file_bytes, file.filename)

    # Call AI
    ai_result = analyze_text(extracted_text)

    # SAFE JSON PARSING (this is the real fix)
    try:
        ai_data = json.loads(ai_result)
    except Exception:
        ai_data = {
            "document_type": "Unknown",
            "parties": [],
            "summary": ai_result[:500] if ai_result else ""
        }

    return {
        "status": "success",
        "filename": file.filename,
        "size_bytes": len(file_bytes),
        "ai_data": ai_data
    }
