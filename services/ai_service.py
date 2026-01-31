import json
import requests
from config import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT
)

def analyze_text(text: str):
    if not text.strip():
        return {"document_type": "Other"}

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=2024-02-15-preview"

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }

    prompt = f"""
Classify this document into ONE of these categories or "Other":

Invoice, Purchase Order, Receipt, Resume, Agreement, Report, Certificate,
Authorization Letter, Delivery Note, Salary Slip, Promotional Brochure,
Inventory Report, Payment Advice

Return ONLY valid JSON:
{{ "document_type": "..." }}

Document:
{text[:4000]}
"""

    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 100
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
        parsed = json.loads(raw)
        return parsed
    except Exception as e:
        print("AI failed:", e)
        return {"document_type": "Other"}
