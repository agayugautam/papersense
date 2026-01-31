# services/ai_service.py

import os
import json
import requests

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")


SYSTEM_PROMPT = """
You are PaperSense, an enterprise-grade document intelligence system.

Your job is to analyze the content of a business document and return:

1. document_type: one of:
   - invoice
   - receipt
   - purchase_order
   - contract
   - agreement
   - resume
   - bank_statement
   - legal_notice
   - insurance
   - shipping_document
   - tax_document
   - financial_report
   - id_document
   - certificate
   - email
   - other

2. parties_involved: list of people or organizations mentioned.

3. summary: 2–3 lines short summary.

4. detailed_summary: 5–10 lines detailed summary.

5. confidence: float between 0 and 1.

Rules:
- Use "other" only if no category clearly fits.
- If text looks like a CV, classify as resume.
- If text contains invoice numbers, totals, VAT, amounts → invoice.
- If it contains legal clauses → contract or agreement.
- If confidence < 0.6, set document_type to "other".

Return ONLY valid JSON in this format:

{
  "document_type": "...",
  "parties_involved": ["..."],
  "summary": "...",
  "detailed_summary": "...",
  "confidence": 0.00
}
"""


def analyze_text(extracted_text: str):
    """
    Main AI classification function
    """

    if not extracted_text or len(extracted_text.strip()) < 50:
        return {
            "document_type": "other",
            "parties_involved": [],
            "summary": "Not enough readable text.",
            "detailed_summary": "The document did not contain enough extractable text for analysis.",
            "confidence": 0.0
        }

    # Limit text to avoid token explosion
    extracted_text = extracted_text[:12000]

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }

    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},

            # Few-shot learning examples (VERY IMPORTANT)
            {"role": "user", "content": "Invoice No: INV-1023\nTotal Amount: QAR 450\nVAT: QAR 22.5\nCustomer: ABC Trading"},
            {"role": "assistant", "content": json.dumps({
                "document_type": "invoice",
                "parties_involved": ["ABC Trading"],
                "summary": "Invoice issued by ABC Trading for goods worth QAR 450.",
                "detailed_summary": "This document is an invoice with invoice number INV-1023 showing a total payable amount of QAR 450 including VAT of QAR 22.5.",
                "confidence": 0.95
            })},

            {"role": "user", "content": "Name: John Smith\nExperience: 5 years in marketing\nSkills: SEO, Sales, CRM"},
            {"role": "assistant", "content": json.dumps({
                "document_type": "resume",
                "parties_involved": ["John Smith"],
                "summary": "Resume of John Smith highlighting marketing experience.",
                "detailed_summary": "This document is a professional resume for John Smith outlining his experience in marketing, skills in SEO, sales, and CRM.",
                "confidence": 0.96
            })},

            {"role": "user", "content": extracted_text}
        ],
        "temperature": 0.2,
        "max_tokens": 700
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        raw_output = data["choices"][0]["message"]["content"]
        print("AI RAW OUTPUT:", raw_output)

        result = json.loads(raw_output)

        # Safety layer
        if result.get("confidence", 0) < 0.6:
            result["document_type"] = "other"

        return result

    except Exception as e:
        print("AI failed:", repr(e))
        return {
            "document_type": "other",
            "parties_involved": [],
            "summary": "AI classification failed.",
            "detailed_summary": "The AI service encountered an error and could not classify the document.",
            "confidence": 0.0
        }
