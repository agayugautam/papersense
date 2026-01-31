import json
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT
)

ALLOWED_CATEGORIES = [
    "Product Display",
    "Product Display Image",
    "Product Packaging",
    "Promotional Brochure",
    "Promotional Display",
    "Promotional Offer",
    "Purchase Order",
    "Purchase Return Voucher",
    "Receipt Confirmation Report",
    "Resume",
    "Retail Mart Promotional Flyer",
    "Retail Promotion Display",
    "Salary Slip",
    "Sales and Commission Report",
    "Service Agreement (Renewal)",
    "Shipment Inspection Report",
    "Sofa Re-upholstery Price List",
    "Task Checklist",
    "Transaction Details Report",
    "Transaction Report",
    "Vendor Delivery Schedule",
    "WOQODe Customer Vehicle Details",
    "Addition of New Vehicles Request",
    "Agreement for the Opening Credit Account",
    "Authorization Letter",
    "Automated Stock Report",
    "Bean Bag Specifications",
    "Business Development Agreement",
    "Business Development and Supply Agreement",
    "Certificate of Analysis",
    "Certificate of Origin",
    "Credit Facility Request Letter",
    "Customer Log",
    "Customs Declaration",
    "Delivery Note",
    "Food Shipment Inspection Report",
    "Form of Supply Agreement",
    "GWC Outbound Order Form",
    "Image Metadata",
    "Indemnity Letter",
    "Inventory Report",
    "Invoice",
    "Kids Catalogue",
    "License Agreement",
    "Local Purchase Order",
    "Local Supply Agreement",
    "Merchant Transaction Log",
    "Ministry of Justice Lawyer Identification Card",
    "Notification",
    "Order Allocation Report",
    "Payment Advice",
    "Payment Confirmation",
    "Payment Reminder",
    "Other"
]

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-15-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def analyze_text(text: str):
    if not text or not text.strip():
        return {"document_type": "Other"}

    try:
        categories_str = "\n".join(ALLOWED_CATEGORIES)

        prompt = f"""
You are an enterprise document classification system.

You must classify the document into EXACTLY ONE of the following categories:

{categories_str}

Rules:
- You must return valid JSON only.
- You must return exactly one category from the list.
- If nothing matches clearly, return "Other".

Return format:
{{ "document_type": "<one category>" }}

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

        doc_type = data.get("document_type", "Other")

        if doc_type not in ALLOWED_CATEGORIES:
            return {"document_type": "Other"}

        return {"document_type": doc_type}

    except Exception as e:
        print("AI CLASSIFICATION FAILED:", repr(e))
        return {"document_type": "Other"}
