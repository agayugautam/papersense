from sqlalchemy import Column, Integer, String, Float
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    document_type = Column(String, index=True)
    size_mb = Column(Float)
    content = Column(String)
