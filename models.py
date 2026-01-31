from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    document_type = Column(String, default="Other")
    parties = Column(String)
    summary = Column(Text)
    detailed_summary = Column(Text)
    size_mb = Column(Float)
    blob_path = Column(String)
