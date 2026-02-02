import io
import pdfplumber
from docx import Document
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

from config import settings
from services.ai_service import ai_service

# Initialize Azure Client using lowercase settings
client = DocumentAnalysisClient(
    endpoint=settings.azure_form_recognizer_endpoint,
    credential=AzureKeyCredential(settings.azure_form_recognizer_key)
)

class ExtractionService:
    async def ingest_document(self, file_bytes: bytes, filename: str):
        ext = filename.lower().split(".")[-1]
        raw_text = ""

        try:
            # -------- PDF (Hybrid) --------
            if ext == "pdf":
                raw_text = self.extract_pdf_text(file_bytes)
                # If extraction is poor (less than 50 chars), fallback to Azure OCR
                if len(raw_text.strip()) < 50:
                    raw_text = self.extract_with_azure(file_bytes)

            # -------- Word --------
            elif ext == "docx":
                raw_text = self.extract_docx_text(file_bytes)

            # -------- Plain Text / CSV --------
            elif ext in ["csv", "txt", "log"]:
                raw_text = file_bytes.decode('utf-8', errors='ignore')

            # -------- Images & Fallback --------
            else:
                raw_text = self.extract_with_azure(file_bytes)

        except Exception as e:
            print(f"Extraction error for {filename}: {repr(e)}")
            raw_text = ""

        # Send to AI for classification and summary
        analysis = await ai_service.analyze_text(raw_text)
        return {"content": raw_text, "analysis": analysis}

    def extract_pdf_text(self, file_bytes: bytes) -> str:
        text = ""
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except:
            pass
        return text

    def extract_docx_text(self, file_bytes: bytes) -> str:
        try:
            doc = Document(io.BytesIO(file_bytes))
            return "\n".join([p.text for p in doc.paragraphs])
        except:
            return ""

    def extract_with_azure(self, file_bytes: bytes) -> str:
        poller = client.begin_analyze_document("prebuilt-read", document=file_bytes)
        result = poller.result()
        text = ""
        for page in result.pages:
            for line in page.lines:
                text += line.content + "\n"
        return text

extraction_service = ExtractionService()