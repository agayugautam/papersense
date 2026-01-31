# main.py
import os
import uvicorn
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

# THIS PART IS CRITICAL FOR RAILWAY
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
