from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_API_VERSION,
)
import json

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

SYSTEM_PROMPT = """
You are an enterprise document intelligence system.
Given raw extracted text from a document, return JSON:
{
  "document_type": one of [Invoice, Resume, Contract, Indemnity Letter, Report, Email, PO, Receipt, Other],
  "parties": ["Party A", "Party B"],
  "summary": "short summary",
  "detailed_summary": "long summary"
}
Only return valid JSON.
"""

def analyze_text(text: str):
    response = client.chat.completions.create(
        deployment_id=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text[:12000]},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content
    return json.loads(content)
