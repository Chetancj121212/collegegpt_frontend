import os
import tempfile
from typing import List, Optional, BinaryIO
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureBlobManager:
    """
    A manager class for interacting with Azure Blob Storage.
    Handles uploading, downloading, and managing uploaded documents.
    """
    
    def __init__(self, connection_string: str, container_name: str):
        """
        Initialize the Azure Blob manager.
        
        Args:
            connection_string (str): Azure Storage connection string
            container_name (str): Name of the blob container for uploaded documents
        """
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Ensure container exists
        self._ensure_container_exists()
        
    def _ensure_container_exists(self):
        """
        Create the container if it doesn't exist.
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.create_container()
            logger.info(f"Created new container: {self.container_name}")
        except ResourceExistsError:
            logger.info(f"Container already exists: {self.container_name}")
        except Exception as e:
            logger.error(f"Error ensuring container exists: {e}")
            raise
    
    def upload_file(self, file_content: BinaryIO, filename: str, overwrite: bool = True) -> tuple[str, str]:
        """
        Upload a file to Azure Blob Storage.
        
        Args:
            file_content (BinaryIO): File content to upload
            filename (str): Name of the file
            overwrite (bool): Whether to overwrite if file exists
            
        Returns:
            tuple[str, str]: (Blob URL of the uploaded file, actual blob name)
        """
        try:
            # Add timestamp to filename to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"{timestamp}_{filename}"
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Upload file
            blob_client.upload_blob(file_content, overwrite=overwrite)
            
            logger.info(f"Successfully uploaded file to blob: {blob_name}")
            return blob_client.url, blob_name
            
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {e}")
            raise
    
    def download_file(self, blob_name: str) -> Optional[bytes]:
        """
        Download a file from Azure Blob Storage.
        
        Args:
            blob_name (str): Name of the blob to download
            
        Returns:
            Optional[bytes]: File content as bytes, None if error
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            download_stream = blob_client.download_blob()
            file_content = download_stream.readall()
            
            logger.info(f"Successfully downloaded blob: {blob_name}")
            return file_content
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name}")
            return None
        except Exception as e:
            logger.error(f"Error downloading blob {blob_name}: {e}")
            return None
    
    def download_file_to_temp(self, blob_name: str) -> Optional[str]:
        """
        Download a file from Azure Blob Storage to a temporary local file.
        
        Args:
            blob_name (str): Name of the blob to download
            
        Returns:
            Optional[str]: Path to the temporary file, None if error
        """
        try:
            file_content = self.download_file(blob_name)
            if file_content is None:
                return None
            
            # Create temporary file
            file_extension = os.path.splitext(blob_name)[1]
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=file_extension
            )
            
            # Write content to temporary file
            temp_file.write(file_content)
            temp_file.close()
            
            logger.info(f"Blob downloaded to temporary location: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error downloading blob to temp: {e}")
            return None
    
    def list_blobs(self, prefix: str = None) -> List[dict]:
        """
        List all blobs in the container.
        
        Args:
            prefix (str): Optional prefix to filter blobs
            
        Returns:
            List[dict]: List of blob information
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blobs_info = []
            
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            for blob in blobs:
                blob_info = {
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified,
                    "content_type": blob.content_settings.content_type if blob.content_settings else None,
                    "url": f"{self.blob_service_client.url}/{self.container_name}/{blob.name}"
                }
                blobs_info.append(blob_info)
            
            logger.info(f"Found {len(blobs_info)} blobs in container")
            return blobs_info
            
        except Exception as e:
            logger.error(f"Error listing blobs: {e}")
            return []
    
    def delete_blob(self, blob_name: str) -> bool:
        """
        Delete a blob from Azure Blob Storage.
        
        Args:
            blob_name (str): Name of the blob to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            logger.info(f"Successfully deleted blob: {blob_name}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found for deletion: {blob_name}")
            return False
        except Exception as e:
            logger.error(f"Error deleting blob {blob_name}: {e}")
            return False
    
    def get_blob_info(self, blob_name: str) -> Optional[dict]:
        """
        Get information about a specific blob.
        
        Args:
            blob_name (str): Name of the blob
            
        Returns:
            Optional[dict]: Blob information
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            properties = blob_client.get_blob_properties()
            
            return {
                "name": blob_name,
                "size": properties.size,
                "last_modified": properties.last_modified,
                "content_type": properties.content_settings.content_type,
                "url": blob_client.url,
                "container": self.container_name
            }
            
        except Exception as e:
            logger.error(f"Error getting blob info for {blob_name}: {e}")
            return None
    
    def generate_download_url(self, blob_name: str, expiry_hours: int = 24) -> Optional[str]:
        """
        Generate a temporary download URL for a blob.
        
        Args:
            blob_name (str): Name of the blob
            expiry_hours (int): Hours until URL expires
            
        Returns:
            Optional[str]: Download URL
        """
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            from datetime import datetime, timedelta
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=blob_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            
            download_url = f"{blob_client.url}?{sas_token}"
            logger.info(f"Generated download URL for {blob_name} (expires in {expiry_hours}h)")
            return download_url
            
        except Exception as e:
            logger.error(f"Error generating download URL for {blob_name}: {e}")
            return None
