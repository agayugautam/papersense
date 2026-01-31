from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    size_mb = Column(Float)

    parties_involved = Column(Text)     # JSON string
    summary = Column(Text)
    detailed_summary = Column(Text)
    keywords = Column(Text)             # JSON string

    content = Column(Text)
