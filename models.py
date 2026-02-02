from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from database import Base
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    blob_path = Column(String)
    file_type = Column(String)
    size_mb = Column(Float, default=0.0)
    content = Column(Text)
    document_type = Column(String, default="Other") # <--- Must match React
    summary = Column(Text)
    detailed_summary = Column(Text)
    confidence = Column(Float, default=0.0)
    language = Column(String, default="en")
    parties = Column(JSON)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)