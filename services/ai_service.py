import requests
import json
from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT

def analyze_document(text: str):
    prompt = f"""
Extract:
1. document_type
2. parties
3. summary
4. detailed_summary

Return strict JSON.

TEXT:
{text[:4000]}
"""

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=2024-02-15-preview"
    headers = {"api-key": AZURE_OPENAI_KEY, "Content-Type": "application/json"}

    payload = {
        "messages": [
            {"role": "system", "content": "You are a document intelligence engine"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 500
    }

    r = requests.post(url, headers=headers, json=payload)
    data = r.json()

    try:
        return json.loads(data["choices"][0]["message"]["content"])
    except:
        return {
            "document_type": "Other",
            "parties": "",
            "summary": "",
            "detailed_summary": ""
        }
