# services/ai_service.py

import os
import json
import re
import requests
from typing import Dict, Any
from config import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT
)

AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2024-02-15-preview"
)


def _post_chat(prompt: str) -> str:
    """
    Calls Azure OpenAI Chat Completions.
    Returns raw text from the model.
    """
    if not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY and AZURE_OPENAI_DEPLOYMENT):
        raise RuntimeError("Azure OpenAI config missing")

    url = (
        f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/"
        f"{AZURE_OPENAI_DEPLOYMENT}/chat/completions"
        f"?api-version={AZURE_OPENAI_API_VERSION}"
    )

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY,
    }

    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are an enterprise document intelligence system."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 700,
        "temperature": 0
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    try:
        text = data["choices"][0]["message"]["content"]
    except Exception:
        text = json.dumps(data)

    return text.strip()


def _extract_json(raw: str) -> Dict[str, Any]:
    """
    Extract JSON safely from model output.
    Handles cases where model wraps JSON in text.
    """
    # Direct JSON
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Find first {...} block
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    raise ValueError("Could not parse JSON from model output")


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Main function used by your system.
    Returns:
    {
        document_type,
        parties_involved,
        summary,
        detailed_summary
    }
    """

    if not text or len(text.strip()) < 50:
        return {
            "document_type": "Other",
            "parties_involved": [],
            "summary": "",
            "detailed_summary": ""
        }

    prompt = f"""
You are an enterprise document classification and understanding system.

You MUST classify the document into exactly ONE of the following types:

Resume  
Invoice  
Purchase Order  
Agreement  
Contract  
Report  
Certificate  
Receipt  
Payslip  
Other  

STRICT RULES:
- If the document contains a person's profile, job history, skills, education, career summary → document_type = "Resume"
- If it contains billing amounts, totals, taxes → "Invoice"
- If it contains legal obligations, clauses, parties → "Agreement" or "Contract"
- If it contains structured business or analytical data → "Report"
- If it contains salary breakdown → "Payslip"
- If official proof → "Certificate"
- Only use "Other" if nothing fits.

Return STRICT JSON with EXACTLY these keys:

{{
  "document_type": "...",
  "parties_involved": ["..."],
  "summary": "...",
  "detailed_summary": "..."
}}

Definitions:
- parties_involved → person names, company names, organizations
- summary → 2-3 lines
- detailed_summary → 5-8 lines

Document text:
{text[:4000]}
"""

    try:
        raw = _post_chat(prompt)
        parsed = _extract_json(raw)
    except Exception as e:
        print("AI failed:", repr(e))
        return {
            "document_type": "Other",
            "parties_involved": [],
            "summary": "",
            "detailed_summary": ""
        }

    # Hard safety guarantees
    result = {
        "document_type": parsed.get("document_type", "Other"),
        "parties_involved": parsed.get("parties_involved", []),
        "summary": parsed.get("summary", ""),
        "detailed_summary": parsed.get("detailed_summary", "")
    }

    # Final guardrail
    if not result["document_type"]:
        result["document_type"] = "Other"

    if not isinstance(result["parties_involved"], list):
        result["parties_involved"] = []

    return result
