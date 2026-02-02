import os
import uuid
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Document as DBDocument, DocumentChunk
from services.blob_service import upload_to_blob
from services.llm_service import classify_and_summarize
from services.embedding_service import embed_text


def ingest_document(file_path, filename):
    db: Session = SessionLocal()

    # Upload to Azure Blob
    blob_path, blob_url, size_mb = upload_to_blob(file_path, filename)

    # Extract + classify
    classification = classify_and_summarize(file_path)

    doc_type = classification.get("document_type", "Other")
    summary = classification.get("summary", "")
    detailed_summary = classification.get("detailed_summary", "")

    # Save document
    db_document = DBDocument(
        filename=filename,
        document_type=doc_type,
        summary=summary,
        detailed_summary=detailed_summary,
        blob_path=blob_path,
        blob_url=blob_url,
        size_mb=size_mb,
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Chunk + embed
    chunks = classification.get("chunks", [])

    for chunk in chunks:
        emb = embed_text(chunk)
        db_chunk = DocumentChunk(
            document_id=db_document.id,
            content=chunk,
            embedding=str(emb)
        )
        db.add(db_chunk)

    db.commit()
    return db_document.id
