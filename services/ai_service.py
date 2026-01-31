# services/ai_service.py

import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

def analyze_text(text: str):
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": """You are a document classification engine.
Return JSON:
{
  "document_type": "...",
  "parties": ["..."],
  "summary": "...",
  "detailed_summary": "..."
}
"""
            },
            {
                "role": "user",
                "content": text[:12000]
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content
