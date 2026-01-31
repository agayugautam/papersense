from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String)
    document_type = Column(String)
    size_mb = Column(Float)
    content = Column(Text)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
