import os
import json
import re
import requests
from config import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT
)

AZURE_OPENAI_API_VERSION = "2024-02-15-preview"

ALLOWED_DOCUMENT_TYPES = [
    "Product Display","Product Display Image","Product Packaging",
    "Promotional Brochure","Promotional Display","Promotional Offer",
    "Purchase Order","Purchase Return Voucher","Receipt Confirmation Report",
    "Resume","Retail Mart Promotional Flyer","Retail Promotion Display",
    "Salary Slip","Sales and Commission Report","Service Agreement (Renewal)",
    "Shipment Inspection Report","Sofa Re-upholstery Price List","Task Checklist",
    "Transaction Details Report","Transaction Report","Vendor Delivery Schedule",
    "WOQODe Customer Vehicle Details","Addition of New Vehicles Request",
    "Agreement for the Opening Credit Account","Authorization Letter",
    "Automated Stock Report","Bean Bag Specifications",
    "Business Development Agreement","Business Development and Supply Agreement",
    "Certificate of Analysis","Certificate of Origin",
    "Credit Facility Request Letter","Customer Log","Customs Declaration",
    "Delivery Note","Food Shipment Inspection Report",
    "Form of Supply Agreement","GWC Outbound Order Form",
    "Image Metadata","Indemnity Letter","Inventory Report","Invoice",
    "Kids Catalogue","License Agreement","Local Purchase Order",
    "Local Supply Agreement","Merchant Transaction Log",
    "Ministry of Justice Lawyer Identification Card","Notification",
    "Order Allocation Report","Payment Advice","Payment Confirmation",
    "Payment Reminder","Other"
]

def _post_chat(prompt: str) -> str:
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a document intelligence engine."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800,
        "temperature": 0
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _extract_json(raw: str):
    try:
        return json.loads(raw)
    except:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("No JSON")


def analyze_text(text: str):
    if not text.strip():
        return {
            "document_type": "Other",
            "parties_involved": [],
            "summary": "",
            "detailed_summary": "",
            "keywords": []
        }

    categories = ", ".join(ALLOWED_DOCUMENT_TYPES)

    prompt = f"""
Extract structured intelligence.

Return STRICT JSON with:
- document_type (one of: {categories})
- parties_involved (array)
- summary (1-2 lines)
- detailed_summary (5-8 lines)
- keywords (array)

If unsure: document_type = "Other"

Document:
{text[:5000]}
"""

    try:
        raw = _post_chat(prompt)
        data = _extract_json(raw)

        if data.get("document_type") not in ALLOWED_DOCUMENT_TYPES:
            data["document_type"] = "Other"

        return {
            "document_type": data.get("document_type", "Other"),
            "parties_involved": data.get("parties_involved", []),
            "summary": data.get("summary", ""),
            "detailed_summary": data.get("detailed_summary", ""),
            "keywords": data.get("keywords", [])
        }

    except Exception as e:
        print("AI ERROR:", e)
        return {
            "document_type": "Other",
            "parties_involved": [],
            "summary": "",
            "detailed_summary": "",
            "keywords": []
        }
