from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import settings
from services.ai_service import ai_service

class ExtractionService:
    def __init__(self):
        self.client = DocumentAnalysisClient(
            endpoint=settings.azure_form_recognizer_endpoint,
            credential=AzureKeyCredential(settings.azure_form_recognizer_key)
        )

    async def ingest_document(self, file_content: bytes):
        poller = self.client.begin_analyze_document("prebuilt-read", file_content)
        result = poller.result()
        
        raw_text = "\n".join([line.content for page in result.pages for line in page.lines])
        
        if not raw_text.strip():
            return {"content": "", "analysis": {"doc_type": "Other", "summary": "Empty Document"}}

        analysis = await ai_service.analyze_text(raw_text)
        return {"content": raw_text, "analysis": analysis}

extraction_service = ExtractionService()