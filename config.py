# config.py

import os
from dotenv import load_dotenv

# Force load .env from project root
load_dotenv(dotenv_path=".env", override=True)


def require_env(key: str):
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required env variable: {key}")
    return value


# ===========================
# Local Database (ignored now, SQLite used)
# ===========================

DATABASE_URL = os.getenv("DATABASE_URL")


# ===========================
# Azure Blob Storage
# ===========================

AZURE_STORAGE_CONNECTION_STRING = require_env("AZURE_STORAGE_CONNECTION_STRING")
AZURE_BLOB_CONTAINER = require_env("AZURE_BLOB_CONTAINER")


# ===========================
# Azure OpenAI
# ===========================

AZURE_OPENAI_ENDPOINT = require_env("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = require_env("AZURE_OPENAI_KEY")
AZURE_OPENAI_API_VERSION = require_env("AZURE_OPENAI_API_VERSION")

# Chat model deployment
AZURE_OPENAI_DEPLOYMENT = require_env("AZURE_OPENAI_DEPLOYMENT")

# Embedding deployment (THIS WAS YOUR BUG)
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = require_env("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")


# ===========================
# Azure OCR
# ===========================

AZURE_FORM_RECOGNIZER_ENDPOINT = require_env("AZURE_FORM_RECOGNIZER_ENDPOINT")
AZURE_FORM_RECOGNIZER_KEY = require_env("AZURE_FORM_RECOGNIZER_KEY")


# ===========================
# Debug Print (one-time at startup)
# ===========================

print("=== PaperSense Config Loaded ===")
print("AZURE_OPENAI_DEPLOYMENT =", AZURE_OPENAI_DEPLOYMENT)
print("AZURE_OPENAI_EMBEDDING_DEPLOYMENT =", AZURE_OPENAI_EMBEDDING_DEPLOYMENT)
print("AZURE_BLOB_CONTAINER =", AZURE_BLOB_CONTAINER)
print("================================")
