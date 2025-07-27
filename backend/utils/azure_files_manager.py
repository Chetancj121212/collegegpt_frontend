import os
import tempfile
from typing import List, Optional
from azure.storage.fileshare import ShareFileClient, ShareDirectoryClient
from azure.core.exceptions import ResourceNotFoundError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureFilesManager:
    """
    A manager class for interacting with Azure Files storage.
    Handles downloading, listing, and processing PDF files from Azure Files.
    """
    
    def __init__(self, connection_string: str, share_name: str):
        """
        Initialize the Azure Files manager.
        
        Args:
            connection_string (str): Azure Storage connection string
            share_name (str): Name of the Azure Files share
        """
        self.connection_string = connection_string
        self.share_name = share_name
        
    def list_pdf_files(self, directory_path: str = "") -> List[str]:
        """
        List all PDF files in the specified directory of Azure Files.
        
        Args:
            directory_path (str): Path to the directory in Azure Files (empty for root)
            
        Returns:
            List[str]: List of PDF file paths
        """
        try:
            # Create directory client
            if directory_path:
                dir_client = ShareDirectoryClient.from_connection_string(
                    conn_str=self.connection_string,
                    share_name=self.share_name,
                    directory_path=directory_path
                )
            else:
                # For root directory
                dir_client = ShareDirectoryClient.from_connection_string(
                    conn_str=self.connection_string,
                    share_name=self.share_name,
                    directory_path=""
                )
            
            pdf_files = []
            
            # List all files and directories
            for item in dir_client.list_directories_and_files():
                if item.is_directory:
                    # Recursively search subdirectories
                    sub_path = f"{directory_path}/{item.name}" if directory_path else item.name
                    pdf_files.extend(self.list_pdf_files(sub_path))
                else:
                    # Check if it's a PDF file
                    if item.name.lower().endswith('.pdf'):
                        file_path = f"{directory_path}/{item.name}" if directory_path else item.name
                        pdf_files.append(file_path)
            
            logger.info(f"Found {len(pdf_files)} PDF files in Azure Files")
            return pdf_files
            
        except ResourceNotFoundError:
            logger.warning(f"Directory not found: {directory_path}")
            return []
        except Exception as e:
            logger.error(f"Error listing PDF files: {e}")
            return []
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """
        Download a file from Azure Files.
        
        Args:
            file_path (str): Path to the file in Azure Files
            
        Returns:
            Optional[bytes]: File content as bytes, None if error
        """
        try:
            # Create file client
            file_client = ShareFileClient.from_connection_string(
                conn_str=self.connection_string,
                share_name=self.share_name,
                file_path=file_path
            )
            
            # Download file
            download_stream = file_client.download_file()
            file_content = download_stream.readall()
            
            logger.info(f"Successfully downloaded file: {file_path}")
            return file_content
            
        except ResourceNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error downloading file {file_path}: {e}")
            return None
    
    def download_file_to_temp(self, file_path: str) -> Optional[str]:
        """
        Download a file from Azure Files to a temporary local file.
        
        Args:
            file_path (str): Path to the file in Azure Files
            
        Returns:
            Optional[str]: Path to the temporary file, None if error
        """
        try:
            file_content = self.download_file(file_path)
            if file_content is None:
                return None
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=os.path.splitext(file_path)[1]
            )
            
            # Write content to temporary file
            temp_file.write(file_content)
            temp_file.close()
            
            logger.info(f"File downloaded to temporary location: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Error downloading file to temp: {e}")
            return None
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about a file in Azure Files.
        
        Args:
            file_path (str): Path to the file in Azure Files
            
        Returns:
            Optional[dict]: File information including size, last modified, etc.
        """
        try:
            file_client = ShareFileClient.from_connection_string(
                conn_str=self.connection_string,
                share_name=self.share_name,
                file_path=file_path
            )
            
            properties = file_client.get_file_properties()
            
            return {
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": properties.size,
                "last_modified": properties.last_modified,
                "content_type": properties.content_settings.content_type
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def sync_all_pdfs_to_vector_db(self, vector_db_manager, document_processor, embedding_function):
        """
        Sync all PDF files from Azure Files to the vector database.
        
        Args:
            vector_db_manager: VectorDBManager instance
            document_processor: Function to extract text from PDF
            embedding_function: Function to generate embeddings
        """
        try:
            # Get list of all PDF files
            pdf_files = self.list_pdf_files()
            
            if not pdf_files:
                logger.warning("No PDF files found in Azure Files")
                return
            
            processed_count = 0
            
            for file_path in pdf_files:
                try:
                    logger.info(f"Processing file: {file_path}")
                    
                    # Download file to temporary location
                    temp_file_path = self.download_file_to_temp(file_path)
                    if temp_file_path is None:
                        logger.error(f"Failed to download file: {file_path}")
                        continue
                    
                    # Extract text from PDF
                    document_text = document_processor(temp_file_path)
                    if not document_text:
                        logger.warning(f"No text extracted from: {file_path}")
                        os.unlink(temp_file_path)  # Clean up temp file
                        continue
                    
                    # Chunk the text
                    from utils.document_processor import chunk_text
                    chunks = chunk_text(document_text)
                    if not chunks:
                        logger.warning(f"No chunks created for: {file_path}")
                        os.unlink(temp_file_path)  # Clean up temp file
                        continue
                    
                    # Generate embeddings
                    embeddings = [embedding_function(chunk) for chunk in chunks]
                    
                    # Create metadata
                    metadatas = [
                        {
                            "filename": os.path.basename(file_path),
                            "source": "azure_files",
                            "file_path": file_path,
                            "chunk_index": i
                        } 
                        for i, _ in enumerate(chunks)
                    ]
                    
                    # Add to vector database
                    vector_db_manager.add_documents(chunks, embeddings, metadatas)
                    
                    processed_count += 1
                    logger.info(f"Successfully processed: {file_path}")
                    
                    # Clean up temporary file
                    os.unlink(temp_file_path)
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    # Clean up temp file if it exists
                    if 'temp_file_path' in locals() and temp_file_path and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                    continue
            
            logger.info(f"Successfully processed {processed_count} out of {len(pdf_files)} PDF files")
            
        except Exception as e:
            logger.error(f"Error syncing PDFs to vector database: {e}")
