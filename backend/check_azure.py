import os
from dotenv import load_dotenv
from utils.azure_blob_manager import AzureBlobManager

load_dotenv()
AZURE_BLOB_CONNECTION_STRING = os.getenv('AZURE_BLOB_CONNECTION_STRING')
AZURE_BLOB_CONTAINER_NAME = os.getenv('AZURE_BLOB_CONTAINER_NAME', 'uploaded-documents')

if AZURE_BLOB_CONNECTION_STRING:
    try:
        blob_manager = AzureBlobManager(AZURE_BLOB_CONNECTION_STRING, AZURE_BLOB_CONTAINER_NAME)
        blobs = blob_manager.list_blobs()
        print(f'Total blobs in Azure Storage: {len(blobs)}')
        for blob in blobs:
            print(f'  - {blob["name"]} ({blob["size"]} bytes)')
    except Exception as e:
        print(f'Error accessing Azure Blob Storage: {e}')
else:
    print('Azure Blob Storage not configured')
