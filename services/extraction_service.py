import fitz  # PyMuPDF

def extract_text(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)

    try:
        return file_bytes.decode(errors="ignore")
    except:
        return ""
