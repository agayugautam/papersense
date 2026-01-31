# services/blob_service.py
from azure.storage.blob import BlobServiceClient
from config import AZURE_STORAGE_CONNECTION_STRING, AZURE_BLOB_CONTAINER
import uuid

blob_service = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)

container_client = blob_service.get_container_client(
    AZURE_BLOB_CONTAINER
)

def upload_file(file_bytes: bytes, filename: str) -> str:
    blob_name = f"{uuid.uuid4()}_{filename}"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file_bytes, overwrite=True)
    return blob_name

def download_file(blob_path: str) -> bytes:
    blob_client = container_client.get_blob_client(blob_path)
    return blob_client.download_blob().readall()

def delete_file(blob_path: str):
    blob_client = container_client.get_blob_client(blob_path)
    blob_client.delete_blob()
