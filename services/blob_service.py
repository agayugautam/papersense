from azure.storage.blob import BlobServiceClient
from config import AZURE_STORAGE_CONNECTION_STRING, AZURE_BLOB_CONTAINER
import uuid

blob_service = BlobServiceClient.from_connection_string(
    AZURE_STORAGE_CONNECTION_STRING
)
container = blob_service.get_container_client(AZURE_BLOB_CONTAINER)

def upload_to_azure(file_bytes, filename):
    blob_name = f"{uuid.uuid4()}_{filename}"
    blob_client = container.get_blob_client(blob_name)
    blob_client.upload_blob(file_bytes, overwrite=True)
    return blob_client.url
