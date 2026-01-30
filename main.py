# main.py
from fastapi import FastAPI
from database import Base, engine
from routes import documents, dashboard, search

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PaperSense API")

app.include_router(documents.router, prefix="/api/documents")
app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(search.router, prefix="/api/search")

@app.get("/")
def health():
    return {"status": "PaperSense backend running"}
