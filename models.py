from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    blob_url = Column(String)
    document_type = Column(String, default="Other")
    size_mb = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
