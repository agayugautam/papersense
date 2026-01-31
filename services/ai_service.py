# src/services/ai_service.py
import json
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT
)

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-15-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def analyze_text(text: str):
    # Hard safety
    if not text or not text.strip():
        return {"document_type": "Unknown"}

    try:
        prompt = f"""
Classify this business document.
Return ONLY valid JSON in this format:

{{ "document_type": "Invoice" }}

Document text:
{text[:4000]}
"""

        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={ "type": "json_object" }
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)

        if "document_type" not in data:
            return {"document_type": "Unknown"}

        return data

    except Exception as e:
        print("AI CLASSIFICATION FAILED:", repr(e))
        return {"document_type": "Unknown"}
