# src/services/ai_service.py
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

# Default API version; you can override by env if needed
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

def _post_chat(prompt: str) -> str:
    """
    Calls Azure OpenAI chat completions endpoint (deployment-based).
    Returns raw string content from the model or raises for HTTP errors.
    """
    if not (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY and AZURE_OPENAI_DEPLOYMENT):
        raise RuntimeError("Azure OpenAI config missing (AZURE_OPENAI_ENDPOINT/AZURE_OPENAI_KEY/AZURE_OPENAI_DEPLOYMENT)")

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a document classification assistant. Respond concisely."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    j = resp.json()

    # Extract text generically (Azure style)
    # Some responses: j['choices'][0]['message']['content']
    # Some SDKs differ; we defensively check
    text = None
    try:
        text = j["choices"][0]["message"]["content"]
    except Exception:
        # fallback lookups
        try:
            text = j["choices"][0]["text"]
        except Exception:
            text = json.dumps(j)  # last resort: stringify everything

    if not isinstance(text, str):
        text = str(text)

    return text.strip()


def _extract_json_from_text(raw: str) -> Dict[str, Any]:
    """
    Try to find JSON object inside the model response. If found parse and return.
    Otherwise raise ValueError.
    """
    # Try direct JSON first
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Attempt to find first {...} block
    m = re.search(r"(\{(?:[^{}]|(?R))*\})", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass

    # Attempt to find JSON-like simple key: "value" lines -> convert to JSON
    lines = [ln.strip() for ln in raw.splitlines() if ":" in ln]
    if lines:
        candidate = "{" + ", ".join([f'"{l.split(":",1)[0].strip()}":"{l.split(":",1)[1].strip().strip(\'"\')}"' for l in lines[:10]]) + "}"
        try:
            return json.loads(candidate)
        except Exception:
            pass

    raise ValueError("No JSON found in model output")


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Public function. Returns a dict like {"document_type": "...", ...}
    Always returns a dict (never raises) — on error returns {"document_type":"Unknown","raw":raw}
    """
    # Short-circuit for empty text
    if not text or not text.strip():
        return {"document_type": "Unknown", "raw": ""}

    prompt = f"""
Classify the following document and return a strict JSON object with (at least) this key:
  "document_type": string

Only output valid JSON. Example:
{{ "document_type": "Invoice" }}

Document text:
{text[:4000]}
"""

    try:
        raw = _post_chat(prompt)
    except Exception as e:
        # Log and fallback
        print("AI call failed:", repr(e))
        return {"document_type": "Unknown", "raw": ""}

    # Try parsing JSON from the model output robustly
    try:
        parsed = _extract_json_from_text(raw)
        # Ensure document_type exists
        if "document_type" not in parsed or not parsed.get("document_type"):
            parsed["document_type"] = "Unknown"
        # return parsed (JSON/dict)
        return parsed
    except Exception as e:
        # Parsing failed — return Unknown but keep raw for debugging
        print("AI JSON parse failed:", repr(e), "raw:", raw[:1000])
        return {"document_type": "Unknown", "raw": raw[:2000]}
