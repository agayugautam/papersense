# services/ai_service.py
import json
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_text(text: str):
    try:
        prompt = f"""
Classify this document into a business document type.
Return ONLY valid JSON in this format:

{{
  "document_type": "Invoice"
}}

Text:
{text[:4000]}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw = response.choices[0].message.content.strip()

        # Hard safety
        data = json.loads(raw)

        if "document_type" not in data:
            return {"document_type": "Unknown"}

        return data

    except Exception as e:
        print("AI CLASSIFICATION FAILED:", e)
        return {"document_type": "Unknown"}
