from fastapi import FastAPI, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, get_db
from routes import documents, dashboard, search
from sqlalchemy.orm import Session
from models import Document

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

@app.get("/")
def health():
    return {"status": "PaperSense backend running"}

@app.post("/api/debug/reset-documents")
def reset_documents(db: Session = Depends(get_db)):
    db.query(Document).delete()
    db.commit()
    return {"status": "all documents deleted"}
