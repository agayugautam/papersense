import requests
import json
from config import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT
)

API_VERSION = "2024-02-15-preview"

def call_openai(prompt: str) -> str:
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are a document classifier."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 200
    }

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def analyze_text(text: str):
    if not text.strip():
        return {"document_type": "Unknown"}

    prompt = f"""
Classify this document into one of:
Invoice, Receipt, Resume, Agreement, Report, Order, Image, Other.

Return ONLY valid JSON like:
{{ "document_type": "Invoice" }}

Text:
{text[:3000]}
"""
    try:
        raw = call_openai(prompt)
        return json.loads(raw)
    except:
        return {"document_type": "Other"}
