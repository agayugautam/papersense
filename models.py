# backend/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from pgvector.sqlalchemy import Vector
from database import Base
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    document_type = Column(String)
    parties = Column(String)
    summary = Column(Text)
    detailed_summary = Column(Text)
    size_mb = Column(Float)
    blob_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Correct vector column
    embedding = Column(Vector(1536))
