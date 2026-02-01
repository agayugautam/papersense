from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from database import Base, engine, get_db
from routes import documents, dashboard, search
from sqlalchemy.orm import Session
from models import Document
from fastapi import Depends
from azure.storage.blob import BlobServiceClient
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PaperSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents")
app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(search.router, prefix="/api/search")

# Azure connection string from env
AZURE_CONN = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER = "papersense-documents"

blob_service = BlobServiceClient.from_connection_string(AZURE_CONN)

@app.get("/api/download/{doc_id}")
def download_file(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return {"error": "File not found"}

    blob_path = doc.blob_path
    blob_client = blob_service.get_blob_client(
        container=CONTAINER,
        blob=blob_path
    )

    stream = blob_client.download_blob()

    return StreamingResponse(
        stream.chunks(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{doc.filename}"'
        }
    )

@app.get("/")
def health():
    return {"status": "PaperSense backend running"}
