# schemas.py
from pydantic import BaseModel
from datetime import datetime

class DocumentOut(BaseModel):
    id: str
    filename: str
    document_type: str
    category: str
    summary: str
    detailed_summary: str
    size_mb: float
    blob_path: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
