from azure.storage.blob import BlobServiceClient
import os
from config import AZURE_BLOB_CONNECTION_STRING, AZURE_BLOB_CONTAINER

blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_BLOB_CONNECTION_STRING
)
container_client = blob_service_client.get_container_client(
    AZURE_BLOB_CONTAINER
)


def upload_to_blob(file_path, filename):
    blob_name = f"{os.path.basename(file_path)}"
    blob_client = container_client.get_blob_client(blob_name)

    with open(file_path, "rb") as f:
        blob_client.upload_blob(f, overwrite=True)

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    blob_url = blob_client.url

    return blob_name, blob_url, size_mb
