import requests
import json
from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT

def analyze_text(text: str):
    if not text.strip():
        return "Other"

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=2024-02-15-preview"

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }

    prompt = f"""
You are classifying business documents.
Choose exactly ONE of these types or "Other":

Invoice
Purchase Order
Delivery Note
Indemnity Letter
Authorization Letter
Automated Stock Report
Certificate of Analysis
Certificate of Origin
Inventory Report
Receipt Confirmation Report
Payment Advice
Payment Confirmation
Resume
Service Agreement
Shipment Inspection Report

Only return the type name.

Document:
{text[:3000]}
"""

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 20
    }

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()

    content = r.json()["choices"][0]["message"]["content"]
    return content.strip()
