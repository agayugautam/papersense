from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import documents, dashboard, search

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://papersense.vercel.app",  # your prod frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

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
