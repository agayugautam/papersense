import json
from openai import AzureOpenAI
from config import settings

class AIService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )

    async def analyze_text(self, text: str):
        prompt = f"""
        Strictly classify this document into one of these: {settings.DOCUMENT_TYPES}.
        Important: If it is an ID card, License, or Passport, use 'Identity Document'.
        If it is a receipt or transfer, use 'Receipt'.
        
        Text: {text[:4000]}
        Return JSON with key "document_type" and "summary".
        """
        response = self.client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": "You are a professional JSON classifier."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        
        # --- HARD MAPPING LOGIC ---
        raw = text.lower()
        summary = data.get("summary", "").lower()
        dtype = data.get("document_type", "Other")

        # Force Identity mapping if AI misses but summary finds it
        if any(k in raw or k in summary for k in ["identification", "id card", "valid card", "license"]):
            dtype = "Identity Document"
        elif any(k in raw or k in summary for k in ["purchase order", "lpo"]):
            dtype = "Purchase Order"
        elif "invoice" in raw or "invoice" in summary:
            dtype = "Invoice"

        data["document_type"] = dtype
        return data

    async def extract_search_intent(self, query: str):
        # We strip the 's' from the end of words to handle pluralization (invoice vs invoices)
        clean_query = query.lower().strip()
        if clean_query.endswith('s'):
            stemmed = clean_query[:-1]
        else:
            stemmed = clean_query

        return {
            "keywords": [clean_query, stemmed],
            "doc_types": []
        }

ai_service = AIService()