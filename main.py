from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import documents, dashboard, search

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PaperSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents")
app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(search.router, prefix="/api/search")

@app.get("/")
def health():
    return {"status": "PaperSense backend running"}
