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
        Task: Classify this document into one of these: {settings.DOCUMENT_TYPES}.
        Return ONLY a JSON object with:
        "document_type", "confidence" (number 0-1), "summary", "detailed_summary", "language", "parties"
        
        Text: {text[:4000]}
        """
        response = self.client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": "You are a JSON classifier. Always provide confidence as a float number like 0.95."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        
        # --- TYPE GUARD: Fix the 'High' string to float error ---
        conf = data.get("confidence", 0.0)
        if isinstance(conf, str):
            data["confidence"] = 0.95 if conf.lower() == "high" else 0.5
        
        # --- HIERARCHY OVERRIDE ---
        raw = text.lower()
        dtype = data.get("document_type", "Other")
        
        if any(k in raw for k in ["resume", "cv", "curriculum vitae", "work experience"]):
            dtype = "Resume"
        elif any(k in raw for k in ["customs", "duty", "declaration", "tax receipt"]):
            dtype = "Financial Statement"
        elif any(k in raw for k in ["lpo", "purchase order"]):
            dtype = "Purchase Order"
            
        data["document_type"] = dtype
        return data

    async def extract_search_intent(self, query: str):
        # Optimized for your plural/singular search needs
        q = query.lower().strip()
        stemmed = q[:-1] if q.endswith('s') else q
        return {"keywords": [q, stemmed], "doc_types": []}

ai_service = AIService()