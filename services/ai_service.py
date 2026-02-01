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
    """
    Extract first JSON object from a string.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in AI response")
    return match.group(0)

def extract_search_intent(query: str):
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": """
You are an AI that extracts structured search intent.
Return JSON only.

Fields:
- document_type (Resume, Invoice, Contract, Report, PO, Other)
- min_experience_years (number or null)
- keywords (array of important keywords)
"""
            },
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    return json.loads(content)

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
    print("RAW AI RESPONSE:", raw)

    json_text = extract_json(raw)
    return json.loads(json_text)
