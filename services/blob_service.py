from azure.storage.blob import BlobServiceClient
from config import settings

class BlobService:
    def __init__(self):
        self.client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )

    async def upload_file(self, content: bytes, filename: str) -> str:
        # Get the blob client for the specific file
        blob_client = self.client.get_blob_client(
            container=settings.azure_blob_container, 
            blob=filename
        )
        # Upload to Azure
        blob_client.upload_blob(content, overwrite=True)
        return blob_client.url

# Create the singleton instance
blob_service = BlobService()