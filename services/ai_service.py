# services/ai_service.py
from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
)

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-15-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

def classify_document(content: str):
    system_prompt = """
You are a document classification engine.
Given content, return valid JSON with:
- document_type
- category
- summary
- detailed_summary
"""

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content[:3000]},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
