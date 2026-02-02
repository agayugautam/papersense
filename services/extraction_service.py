import io
import pdfplumber
from docx import Document
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import settings
from services.ai_service import ai_service

# Singleton client initialization
client = DocumentAnalysisClient(
    endpoint=settings.azure_form_recognizer_endpoint,
    credential=AzureKeyCredential(settings.azure_form_recognizer_key)
)

class ExtractionService:
    async def ingest_document(self, file_bytes: bytes, filename: str):
        ext = filename.lower().split(".")[-1]
        raw_text = ""

        try:
            if ext == "pdf":
                raw_text = self._extract_pdf(file_bytes)
                if len(raw_text.strip()) < 50:
                    raw_text = self._extract_azure(file_bytes)
            elif ext == "docx":
                raw_text = self._extract_docx(file_bytes)
            elif ext in ["csv", "txt", "log"]:
                raw_text = file_bytes.decode('utf-8', errors='ignore')
            else:
                raw_text = self._extract_azure(file_bytes)
        except Exception:
            raw_text = self._extract_azure(file_bytes)

        analysis = await ai_service.analyze_text(raw_text)
        return {"content": raw_text, "analysis": analysis}

    def _extract_pdf(self, b: bytes):
        text = ""
        with pdfplumber.open(io.BytesIO(b)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text: text += page_text + "\n"
        return text

    def _extract_docx(self, b: bytes):
        doc = Document(io.BytesIO(b))
        return "\n".join([p.text for p in doc.paragraphs])

    def _extract_azure(self, b: bytes):
        poller = client.begin_analyze_document("prebuilt-read", document=b)
        return "\n".join([l.content for p in poller.result().pages for l in p.lines])

extraction_service = ExtractionService()