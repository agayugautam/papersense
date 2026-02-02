from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import documents, dashboard, search

app = FastAPI(title="PaperSense")

# Initialize database tables
init_db()

# Standard CORS setup to allow your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prefixing routes without trailing slashes
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])

@app.get("/")
def health_check():
    return {"status": "Backend is running"}