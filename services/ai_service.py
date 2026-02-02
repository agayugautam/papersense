# backend/services/ai_service.py

from openai import AzureOpenAI
from config import *
import json
import re

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

SYSTEM_PROMPT = """
You are a strict JSON generator.

Return ONLY a valid JSON object.
No explanations.
No markdown.
No code fences.
No extra text.

Schema:
{
  "document_type": one of ["Invoice","Resume","Contract","Indemnity Letter","Report","Email","PO","Receipt","Other"],
  "parties": ["Party A", "Party B"],
  "summary": "short summary",
  "detailed_summary": "long summary"
}
"""

def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found")
    return match.group(0)

def analyze_text(text: str):
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text[:12000]},
        ],
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()
    json_text = extract_json(raw)
    return json.loads(json_text)

# -------- VECTOR EMBEDDING (FIXED) --------

def generate_embedding(text: str):
    response = client.embeddings.create(
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,  
        input=text
    )
    return response.data[0].embedding
