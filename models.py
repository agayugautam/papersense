from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    document_type = Column(String, default="Other")

    summary = Column(Text)
    detailed_summary = Column(Text)

    blob_path = Column(String)   # path inside container
    blob_url = Column(String)    # full URL (optional but useful)

    size_mb = Column(Float, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("documents.id"))
    content = Column(Text)
    embedding = Column(Text)  # stored as JSON string

    document = relationship("Document", back_populates="chunks")
