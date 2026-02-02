import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "PaperSense"
    DATABASE_URL: str = "sqlite:///./papersense.db"
    
    # Azure OpenAI
    azure_openai_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    
    # Azure Document Intelligence
    azure_form_recognizer_endpoint: str
    azure_form_recognizer_key: str
    
    # Azure Storage
    azure_storage_connection_string: str
    azure_blob_container: str
    
    # STRICT LIST: These must match your Frontend/Dashboard expectations
    DOCUMENT_TYPES: List[str] = [
        "Invoice",
        "Contract",
        "Resume",
        "Purchase Order",
        "Legal Document",
        "Receipt",
        "Financial Statement",
        "Letter",
        "Other"
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = False

settings = Settings()