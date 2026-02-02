# services/ai_service.py

from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_OPENAI_DEPLOYMENT
)
import json
import re

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

SYSTEM_PROMPT = """
You are an Enterprise Document Intelligence classifier.

Your job:
- Read the document.
- Understand its real-world business purpose.
- Classify it into the most appropriate document_type from the list below.

CRITICAL RULE:
- You MUST choose the closest matching type.
- Use "Other" ONLY if absolutely nothing fits.
- Never default to "Other" for normal business documents.

Document Types (Enterprise Ontology):

[
  "Invoice",
  "Receipt",
  "Purchase Order",
  "Sales Order",
  "Quotation",
  "Proforma Invoice",
  "Delivery Note",
  "Bill of Lading",

  "Contract",
  "Service Agreement",
  "Employment Contract",
  "Non-Disclosure Agreement",
  "Indemnity Letter",
  "Legal Notice",
  "Power of Attorney",
  "Affidavit",
  "Memorandum of Understanding",
  "Settlement Agreement",

  "Resume",
  "Experience Letter",
  "Offer Letter",
  "Appointment Letter",
  "Relieving Letter",
  "Payslip",
  "Salary Certificate",
  "Employee Handbook",
  "HR Policy",

  "Bank Statement",
  "Loan Agreement",
  "Credit Report",
  "Tax Return",
  "GST Filing",
  "Income Statement",
  "Balance Sheet",
  "Audit Report",

  "Insurance Policy",
  "Claim Form",
  "Medical Report",
  "Prescription",
  "Fitness Certificate",

  "Email",
  "Business Letter",
  "Cover Letter",
  "Notice",
  "Circular",

  "Project Report",
  "Research Paper",
  "Whitepaper",
  "Technical Documentation",
  "User Manual",
  "Product Specification",

  "Certificate",
  "License",
  "Government ID",
  "Passport",
  "Visa",

  "Other"
]

Return ONLY valid JSON.
No markdown.
No explanations.
No extra text.

Schema:
{
  "document_type": "<one of the above>",
  "parties_involved": ["Party A", "Party B"],
  "relevant_dates": ["YYYY-MM-DD"],
  "summary": "short summary",
  "detailed_summary": "long summary"
}
"""


# ===========================
# Utilities
# ===========================

def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in AI response")
    return match.group(0)


# ===========================
# Public API
# ===========================

def analyze_document(text: str) -> dict:
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text[:12000]},
        ],
        temperature=0.0,  # deterministic classification
    )

    raw = response.choices[0].message.content.strip()
    json_text = extract_json(raw)
    return json.loads(json_text)


def embed_text(text: str) -> list:
    response = client.embeddings.create(
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        input=text
    )
    return response.data[0].embedding
