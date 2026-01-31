from sqlalchemy import Column, Integer, String, Float
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    url = Column(String)
    document_type = Column(String)
    size_mb = Column(Float)
