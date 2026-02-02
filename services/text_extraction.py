import io
import pdfplumber
from docx import Document
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import AZURE_DI_ENDPOINT, AZURE_DI_KEY

client = DocumentAnalysisClient(AZURE_DI_ENDPOINT, AzureKeyCredential(AZURE_DI_KEY))

def extract_text_from_file(file_path: str):
    # Note: Reference uses bytes, so we read the file
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    
    filename = file_path.lower()
    ext = filename.split(".")[-1]

    if ext == "pdf":
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        if len(text.strip()) > 50:
            return text
        return extract_with_azure(file_bytes)

    if ext == "docx":
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])

    return extract_with_azure(file_bytes)

def extract_with_azure(file_bytes: bytes) -> str:
    poller = client.begin_analyze_document("prebuilt-read", document=file_bytes)
    result = poller.result()
    return "\n".join([line.content for page in result.pages for line in page.lines])