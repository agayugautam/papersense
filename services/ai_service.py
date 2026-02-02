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
        # We explicitly put "json" in the system and user message
        prompt = f"""
        Task: Classify this document into one of these: {settings.DOCUMENT_TYPES}.
        Output Requirement: Return the result as a json object with these keys:
        "document_type", "confidence", "summary", "detailed_summary", "language", "parties"
        
        Text: {text[:4000]}
        """
        
        response = self.client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": "You are a professional document classifier that outputs everything in json format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        
        # --- Mandatory Keyword Fallback to ensure correct folder mapping ---
        raw = text.lower()
        dtype = data.get("document_type", "Other")
        
        if any(k in raw for k in ["lpo", "purchase order", "order #"]):
            dtype = "Purchase Order"
        elif any(k in raw for k in ["cv", "resume", "curriculum vitae"]):
            dtype = "Resume"
        elif "invoice" in raw or "inv-" in raw:
            dtype = "Invoice"
            
        data["document_type"] = dtype
        return data

    async def extract_search_intent(self, query: str):
        # Again, including "json" in the messages to satisfy the API
        prompt = f"Extract search keywords from: '{query}'. Return as a json object: {{'keywords': ['{query}'], 'doc_types': []}}"
        
        response = self.client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": "You are a search intent extractor. Always provide json output."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

ai_service = AIService()