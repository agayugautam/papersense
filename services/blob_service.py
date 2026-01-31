from azure.storage.blob import BlobServiceClient
from config import AZURE_STORAGE_CONNECTION_STRING, AZURE_BLOB_CONTAINER

def upload_to_azure(filename: str, data: bytes) -> str:
    print("AZURE UPLOAD:", filename)

    blob_service = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )
    container = blob_service.get_container_client(AZURE_BLOB_CONTAINER)

    try:
        container.create_container()
    except:
        pass

    blob = container.get_blob_client(filename)
    blob.upload_blob(data, overwrite=True)

    print("AZURE UPLOAD SUCCESS")

    return f"{AZURE_BLOB_CONTAINER}/{filename}"
