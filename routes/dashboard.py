# routes/dashboard.py

import os
import json
from fastapi import APIRouter

router = APIRouter()
DATA_FILE = "data/documents.json"

@router.get("/metrics")
def get_metrics():
    if not os.path.exists(DATA_FILE):
        docs = []
    else:
        with open(DATA_FILE, "r") as f:
            docs = json.load(f)

    total = len(docs)
    size = sum(d["size_mb"] for d in docs)

    folders = {}
    for d in docs:
        folders.setdefault(d["document_type"], []).append(d)

    return {
        "total_documents": total,
        "storage_used_mb": round(size, 2),
        "recent_files": docs[-5:],
        "folders": folders
    }
