import os
import requests
import json

# These MUST exist in Render / .env
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


def analyze_text(text: str):
    print("🔥 AI FUNCTION CALLED")
    print("TEXT LENGTH:", len(text))

    # Hard guard: if extraction failed, don't even call AI
    if not text or len(text.strip()) < 50:
        print("⚠️ Text too small, skipping AI")
        return {
            "document_type": "Other",
            "parties": [],
            "summary": "",
            "detailed_summary": ""
        }

    # Correct Azure OpenAI URL
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=2024-02-15-preview"

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }

    prompt = f"""
You are an enterprise document intelligence system.

Classify the document and extract structured information.

Return ONLY valid JSON in this exact format:

{{
  "document_type": "Invoice | Resume | Contract | Indemnity Letter | Report | Email | Purchase Order | Legal Notice | Receipt | Other",
  "parties": ["list of people or companies"],
  "summary": "3-4 line summary",
  "detailed_summary": "8-10 line detailed summary"
}}

Document text:
\"\"\"
{text}
\"\"\"
"""

    payload = {
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        print("AZURE STATUS CODE:", res.status_code)
        res.raise_for_status()

        data = res.json()
        response_text = data["choices"][0]["message"]["content"]

        print("🔥 AI RAW RESPONSE:\n", response_text)

        # This will crash loudly if model doesn't return JSON
        result = json.loads(response_text)

        print("✅ AI PARSED RESULT:", result)

        return result

    except Exception as e:
        print("❌ AI ERROR:", str(e))

        return {
            "document_type": "Other",
            "parties": [],
            "summary": "",
            "detailed_summary": ""
        }
