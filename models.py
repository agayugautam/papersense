# models.py
from sqlalchemy import Column, String, DateTime, Float
from database import Base
import datetime
import uuid

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String)
    document_type = Column(String)
    category = Column(String)
    summary = Column(String)
    detailed_summary = Column(String)
    size_mb = Column(Float)
    blob_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
