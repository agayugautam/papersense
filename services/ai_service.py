from openai import AzureOpenAI
from config import *
import json

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

def analyze_text(text: str):
    response = client.chat.completions.create(
        deployment_id=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Classify and summarize this document and return JSON."},
            {"role": "user", "content": text[:12000]},
        ],
        temperature=0.2,
    )

    return json.loads(response.choices[0].message.content)
