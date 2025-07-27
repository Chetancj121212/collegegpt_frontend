import os
import shutil
import tempfile
import gc
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai

# Import custom utility modules
from utils.document_processor import extract_text_from_pdf, extract_text_from_pptx, chunk_text
from utils.vector_db_manager import VectorDBManager
from utils.azure_files_manager import AzureFilesManager
from utils.azure_blob_manager import AzureBlobManager
from config import (
    EMBEDDING_BATCH_SIZE, 
    MAX_CHUNKS_PER_DOCUMENT, 
    EMBEDDING_MODEL_NAME,
    MEMORY_WARNING_THRESHOLD,
    MEMORY_CRITICAL_THRESHOLD
)

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in the .env file.")

# Azure Files configuration (for existing PDF documents)
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_FILES_SHARE_NAME = os.getenv("AZURE_FILES_SHARE_NAME", "college-documents")

# Azure Blob Storage configuration (for uploaded documents)
AZURE_BLOB_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
AZURE_BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME", "uploaded-documents")

# Local fallback folder for uploaded documents (only used if Azure Blob is not configured)
UPLOAD_FOLDER = "./uploaded_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Create the directory if it doesn't exist

# Define path for ChromaDB persistence
CHROMA_DB_PATH = "./chroma_db"

# Global variables for lazy loading
embedding_model = None
gemini_model = None
db_manager = None

# --- Initialize Services ---
app = FastAPI(title="College Bot API", description="FastAPI backend for College Chatbot with Azure integration") # Create FastAPI application instance

# Configure Google Generative AI (Gemini) with the API key
genai.configure(api_key=GEMINI_API_KEY)

def get_embedding_model():
    """Lazy load the embedding model to save memory."""
    global embedding_model
    if embedding_model is None:
        from sentence_transformers import SentenceTransformer
        # Use a smaller, more memory-efficient model
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device='cpu')
    return embedding_model

def get_gemini_model():
    """Lazy load the Gemini model."""
    global gemini_model
    if gemini_model is None:
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    return gemini_model

def get_db_manager():
    """Lazy load the database manager."""
    global db_manager
    if db_manager is None:
        db_manager = VectorDBManager(db_path=CHROMA_DB_PATH)
    return db_manager

# Initialize Azure Files Manager (optional, only if connection string is provided)
azure_files_manager = None
if AZURE_STORAGE_CONNECTION_STRING:
    azure_files_manager = AzureFilesManager(
        connection_string=AZURE_STORAGE_CONNECTION_STRING,
        share_name=AZURE_FILES_SHARE_NAME
    )
    print(f"✅ Azure Files integration enabled for share: {AZURE_FILES_SHARE_NAME}")
else:
    print("⚠️ Azure Files integration disabled (no connection string provided)")

# Initialize Azure Blob Manager for uploaded documents
azure_blob_manager = None
if AZURE_BLOB_CONNECTION_STRING:
    azure_blob_manager = AzureBlobManager(
        connection_string=AZURE_BLOB_CONNECTION_STRING,
        container_name=AZURE_BLOB_CONTAINER_NAME
    )
    print(f"✅ Azure Blob Storage enabled for container: {AZURE_BLOB_CONTAINER_NAME}")
else:
    print("⚠️ Azure Blob Storage disabled - uploaded documents will be stored locally")

# --- CORS Middleware ---
# This middleware is essential for allowing the frontend (running on a different port/origin)
# to communicate with this FastAPI backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins. In a production environment, you should restrict this
                         # to your frontend's specific origin (e.g., "http://localhost:3000", "https://your-frontend-domain.com").
    allow_credentials=True, # Allow cookies/authentication headers to be sent
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all HTTP headers
)

# --- Helper Functions ---
def get_embedding(text: str) -> list[float]:
    """
    Generates an embedding (vector representation) for the given text
    using the Sentence Transformer model with memory optimization.

    Args:
        text (str): The input text to embed.

    Returns:
        list[float]: A list of floats representing the text embedding.
    """
    model = get_embedding_model()
    embedding = model.encode(text).tolist()
    # Force garbage collection after embedding generation
    gc.collect()
    return embedding

# --- API Endpoints ---

@app.get("/")
async def root():
    """
    Root endpoint to verify the API is running.
    """
    return {
        "message": "College Bot API is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring with memory usage.
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
        
        return {
            "status": "healthy",
            "memory_usage_mb": round(memory_mb, 2),
            "memory_percent": round(process.memory_percent(), 2),
            "azure_files_enabled": azure_files_manager is not None,
            "azure_blob_enabled": azure_blob_manager is not None,
            "gemini_configured": bool(GEMINI_API_KEY),
            "models_loaded": {
                "embedding_model": embedding_model is not None,
                "gemini_model": gemini_model is not None,
                "db_manager": db_manager is not None
            }
        }
    except ImportError:
        return {
            "status": "healthy",
            "memory_usage_mb": "unavailable",
            "azure_files_enabled": azure_files_manager is not None,
            "azure_blob_enabled": azure_blob_manager is not None,
            "gemini_configured": bool(GEMINI_API_KEY)
        }

@app.post("/memory/cleanup")
async def cleanup_memory():
    """
    Endpoint to force garbage collection and clear unused models.
    """
    global embedding_model, gemini_model, db_manager
    
    # Force garbage collection
    gc.collect()
    
    # Optionally clear models (they will be reloaded when needed)
    models_cleared = []
    
    try:
        import psutil
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024
        
        # Clear embedding model if loaded
        if embedding_model is not None:
            embedding_model = None
            models_cleared.append("embedding_model")
        
        gc.collect()
        
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_freed = memory_before - memory_after
        
        return {
            "message": "Memory cleanup completed",
            "models_cleared": models_cleared,
            "memory_freed_mb": round(memory_freed, 2),
            "memory_before_mb": round(memory_before, 2),
            "memory_after_mb": round(memory_after, 2)
        }
    except ImportError:
        return {
            "message": "Memory cleanup completed",
            "models_cleared": models_cleared,
            "memory_info": "unavailable"
        }

@app.post("/upload_document/")
async def upload_document(file: UploadFile = File(...)):
    """
    Endpoint to upload a document (PDF or PPTX), extract its text,
    chunk the text, generate embeddings, and store them in the vector database.
    The file is stored in Azure Blob Storage if configured, otherwise locally.

    Args:
        file (UploadFile): The uploaded file object from the request.

    Returns:
        dict: A message indicating the success of the operation.

    Raises:
        HTTPException: If the file type is unsupported, text extraction fails,
                       chunking fails, or any other processing error occurs.
    """
    # Validate file type
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".pptx")):
        raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF and PPTX are supported.")
    
    temp_file_path = None
    blob_url = None
    blob_name = None
    storage_location = None
    max_retries = 3
    
    try:
        # Read file content
        file_content = await file.read()
        
        if azure_blob_manager:
            # Store in Azure Blob Storage with retry mechanism
            retry_count = 0
            upload_success = False
            
            while retry_count < max_retries and not upload_success:
                try:
                    print(f"🔄 Uploading to Azure Blob Storage (attempt {retry_count + 1}/{max_retries})")
                    blob_url, blob_name = azure_blob_manager.upload_file(
                        file_content=file_content,
                        filename=file.filename,
                        overwrite=True
                    )
                    storage_location = f"Azure Blob: {blob_url}"
                    upload_success = True
                    print(f"✅ Successfully uploaded to blob: {blob_name}")
                    
                except Exception as upload_error:
                    retry_count += 1
                    print(f"❌ Upload attempt {retry_count} failed: {upload_error}")
                    if retry_count >= max_retries:
                        print("⚠️ Max retries reached, falling back to local storage")
                        raise upload_error
                    
            if upload_success:
                # Download to temporary file for processing with retry mechanism
                retry_count = 0
                download_success = False
                
                while retry_count < max_retries and not download_success:
                    try:
                        print(f"🔄 Downloading blob for processing (attempt {retry_count + 1}/{max_retries})")
                        temp_file_path = azure_blob_manager.download_file_to_temp(blob_name)
                        if temp_file_path:
                            download_success = True
                            print(f"✅ Successfully downloaded blob to: {temp_file_path}")
                        else:
                            raise Exception("Download returned None")
                            
                    except Exception as download_error:
                        retry_count += 1
                        print(f"❌ Download attempt {retry_count} failed: {download_error}")
                        if retry_count >= max_retries:
                            raise Exception(f"Failed to download blob after {max_retries} attempts: {download_error}")
        
        # Fallback to local storage if Azure fails or is not configured
        if not temp_file_path:
            print("🔄 Using local storage as fallback")
            file_location = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(file_location, "wb") as buffer:
                buffer.write(file_content)
            temp_file_path = file_location
            storage_location = f"Local: {file_location}"
        
        if not temp_file_path:
            raise HTTPException(status_code=500, detail="Failed to save uploaded file.")

        # Extract text from the file
        print(f"🔄 Extracting text from: {file.filename}")
        document_text = ""
        if file.filename.endswith(".pdf"):
            document_text = extract_text_from_pdf(temp_file_path)
        elif file.filename.endswith(".pptx"):
            document_text = extract_text_from_pptx(temp_file_path)

        if not document_text:
            raise HTTPException(status_code=500, detail="Could not extract text from the document.")

        # Chunk the extracted text
        print(f"🔄 Chunking text from: {file.filename}")
        chunks = chunk_text(document_text)
        if not chunks:
            raise HTTPException(status_code=500, detail="Could not chunk the document text.")

        # Generate embeddings for each text chunk with memory optimization
        print(f"🔄 Generating embeddings for {len(chunks)} chunks")
        
        # Limit chunks if too many
        if len(chunks) > MAX_CHUNKS_PER_DOCUMENT:
            chunks = chunks[:MAX_CHUNKS_PER_DOCUMENT]
            print(f"⚠️ Limited to {MAX_CHUNKS_PER_DOCUMENT} chunks to manage memory")
        
        embeddings = []
        batch_size = EMBEDDING_BATCH_SIZE  # Use config value
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i+batch_size]
            batch_embeddings = [get_embedding(chunk) for chunk in batch_chunks]
            embeddings.extend(batch_embeddings)
            # Force garbage collection after each batch
            gc.collect()
            print(f"   - Processed batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
        
        # Create metadata for each chunk
        metadatas = [
            {
                "filename": file.filename, 
                "chunk_index": i,
                "source": "user_upload",
                "storage_location": storage_location,
                "blob_url": blob_url if azure_blob_manager else None,
                "blob_name": blob_name if azure_blob_manager else None,
                "upload_timestamp": str(os.path.getctime(temp_file_path) if os.path.exists(temp_file_path) else "unknown")
            } 
            for i, _ in enumerate(chunks)
        ]

        # Add the chunks, embeddings, and metadata to ChromaDB
        print(f"🔄 Adding {len(chunks)} chunks to ChromaDB")
        db_manager = get_db_manager()
        db_manager.add_documents(chunks, embeddings, metadatas)

        # Log successful processing
        print(f"✅ Successfully processed and stored: {file.filename}")
        print(f"   - Storage location: {storage_location}")
        print(f"   - Text chunks: {len(chunks)}")
        print(f"   - Embeddings generated: {len(embeddings)}")

        return {
            "message": f"Document '{file.filename}' processed and added to vector DB successfully.",
            "details": {
                "filename": file.filename,
                "chunks_created": len(chunks),
                "embeddings_generated": len(embeddings),
                "storage_type": "Azure Blob Storage" if azure_blob_manager and blob_url else "Local Storage",
                "storage_location": storage_location,
                "blob_url": blob_url if azure_blob_manager else None,
                "blob_name": blob_name if azure_blob_manager else None
            }
        }
        
    except HTTPException as e:
        # Clean up on HTTP error
        if temp_file_path and azure_blob_manager and temp_file_path.startswith(tempfile.gettempdir()):
            # Clean up temp file if it was downloaded from blob
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        elif temp_file_path and not azure_blob_manager:
            # Clean up local file on error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        raise e
        
    except Exception as e:
        # Clean up on general error
        if temp_file_path and azure_blob_manager and temp_file_path.startswith(tempfile.gettempdir()):
            # Clean up temp file if it was downloaded from blob
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        elif temp_file_path and not azure_blob_manager:
            # Clean up local file on error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        print(f"❌ Error during document upload and processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
    
    finally:
        # Clean up temporary files (but keep the permanent storage)
        if temp_file_path and azure_blob_manager and temp_file_path.startswith(tempfile.gettempdir()):
            # Only clean up temp files created for processing, not the permanent storage
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

@app.post("/chat/")
async def chat(query: str = Form(...)):
    """
    Endpoint to handle user chat queries.
    It retrieves relevant context from the vector database and generates a response
    using the Gemini model.

    Args:
        query (str): The user's question or message.

    Returns:
        dict: The generated response from the Gemini model.

    Raises:
        HTTPException: If there's an error during embedding generation,
                       vector database query, or Gemini API call.
    """
    try:
        # Generate embedding for the user's query
        query_embedding = get_embedding(query)
        # Retrieve relevant text chunks from ChromaDB based on the query embedding
        db_manager = get_db_manager()
        relevant_chunks = db_manager.query_documents(query_embedding)

        # Construct the prompt for the Gemini model
        if not relevant_chunks:
            # If no relevant chunks are found, use the query directly
            prompt = f"User: {query}\nAI:"
            print("No relevant chunks found. Using direct query.")
        else:
            # Join the relevant chunks to form the context
            context = "\n".join(relevant_chunks)
            # Create a RAG-style prompt including the context
            prompt = f"Based on the following context, answer the user's question. If the answer is not in the context, state that you don't have enough information.\n\nContext:\n{context}\n\nUser: {query}\nAI:"
            print(f"Relevant chunks found. Prompt sent to Gemini.")

        # Call the Gemini model to generate a response
        gemini_model = get_gemini_model()
        response = gemini_model.generate_content(prompt)
        
        # Force garbage collection after response generation
        gc.collect()
        
        # Return the generated text response
        return {"response": response.text}
    except Exception as e:
        # Catch any errors during chat processing and return a 500 error
        print(f"Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get response: {e}")

@app.get("/uploaded_documents/")
async def list_uploaded_documents():
    """
    Endpoint to list all documents stored in the uploaded_docs folder.
    
    Returns:
        dict: List of uploaded documents with their information.
    """
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            return {"total_files": 0, "files": []}
        
        files_info = []
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                files_info.append({
                    "filename": filename,
                    "file_path": file_path,
                    "size_bytes": file_stat.st_size,
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "upload_time": file_stat.st_ctime,
                    "modified_time": file_stat.st_mtime,
                    "file_type": filename.split('.')[-1].upper() if '.' in filename else "Unknown"
                })
        
        # Sort by upload time (newest first)
        files_info.sort(key=lambda x: x['upload_time'], reverse=True)
        
        return {
            "total_files": len(files_info),
            "files": files_info,
            "storage_location": UPLOAD_FOLDER
        }
        
    except Exception as e:
        print(f"Error listing uploaded documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list uploaded documents: {e}")

@app.delete("/uploaded_documents/{filename}")
async def delete_uploaded_document(filename: str):
    """
    Endpoint to delete a specific uploaded document.
    
    Args:
        filename (str): Name of the file to delete.
        
    Returns:
        dict: Status message.
        
    Raises:
        HTTPException: If file not found or deletion fails.
    """
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")
        
        os.remove(file_path)
        print(f"🗑️ Deleted uploaded document: {filename}")
        
        return {"message": f"Document '{filename}' deleted successfully."}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error deleting document {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {e}")

@app.post("/sync_azure_blobs/")
async def sync_azure_blobs():
    """
    Endpoint to sync all uploaded blobs from Azure Blob Storage to the vector database.
    This will process any blobs that were uploaded but not properly added to ChromaDB.
    
    Returns:
        dict: Status message with number of files processed.
        
    Raises:
        HTTPException: If Azure Blob Storage is not configured or sync fails.
    """
    if not azure_blob_manager:
        raise HTTPException(
            status_code=400, 
            detail="Azure Blob Storage not configured. Please set AZURE_BLOB_CONNECTION_STRING."
        )
    
    try:
        print("Starting Azure Blob Storage sync...")
        
        # Get database manager
        db_manager = get_db_manager()
        
        # Get all blobs from Azure Storage
        blobs = azure_blob_manager.list_blobs()
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for blob_info in blobs:
            blob_name = blob_info["name"]
            
            try:
                # Check if this blob is already processed in ChromaDB
                db_result = db_manager.collection.get(
                    where={"blob_url": blob_name}
                )
                
                if len(db_result["documents"]) > 0:
                    print(f"📋 Skipping {blob_name} - already in ChromaDB")
                    skipped_count += 1
                    continue
                
                print(f"🔄 Processing blob: {blob_name}")
                
                # Download blob to temporary file
                temp_file_path = azure_blob_manager.download_file_to_temp(blob_name)
                
                if not temp_file_path:
                    print(f"❌ Failed to download blob: {blob_name}")
                    error_count += 1
                    continue
                
                # Extract original filename from blob name
                original_filename = blob_name
                if blob_name.startswith("20"):  # Remove timestamp prefix
                    parts = blob_name.split("_", 3)
                    if len(parts) > 3:
                        original_filename = parts[3]
                
                # Extract text from the file
                document_text = ""
                if original_filename.endswith(".pdf"):
                    document_text = extract_text_from_pdf(temp_file_path)
                elif original_filename.endswith(".pptx"):
                    document_text = extract_text_from_pptx(temp_file_path)
                
                if not document_text:
                    print(f"❌ Could not extract text from blob: {blob_name}")
                    error_count += 1
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    continue
                
                # Chunk the extracted text
                chunks = chunk_text(document_text)
                if not chunks:
                    print(f"❌ Could not chunk text from blob: {blob_name}")
                    error_count += 1
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    continue
                
                # Generate embeddings for each text chunk
                embeddings = [get_embedding(chunk) for chunk in chunks]
                
                # Create metadata for each chunk
                metadatas = [
                    {
                        "filename": original_filename,
                        "chunk_index": i,
                        "source": "user_upload_synced",
                        "storage_location": f"Azure Blob: {blob_info['url']}",
                        "blob_url": blob_info['url'],
                        "blob_name": blob_name,
                        "sync_timestamp": str(os.path.getctime(temp_file_path) if os.path.exists(temp_file_path) else "unknown")
                    } 
                    for i, _ in enumerate(chunks)
                ]
                
                # Add the chunks, embeddings, and metadata to ChromaDB
                db_manager.add_documents(chunks, embeddings, metadatas)
                
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                
                processed_count += 1
                print(f"✅ Successfully processed blob: {blob_name} ({len(chunks)} chunks)")
                
            except Exception as e:
                print(f"❌ Error processing blob {blob_name}: {e}")
                error_count += 1
                continue
        
        return {
            "message": f"Azure Blob sync completed. Processed: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}",
            "details": {
                "total_blobs": len(blobs),
                "processed": processed_count,
                "skipped": skipped_count,
                "errors": error_count
            }
        }
        
    except Exception as e:
        print(f"Error during Azure Blob sync: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync Azure Blobs: {e}")

@app.post("/sync_azure_files/")
async def sync_azure_files():
    """
    Endpoint to sync all PDF files from Azure Files to the vector database.
    This will download all PDFs, extract text, and add them to ChromaDB.
    
    Returns:
        dict: Status message with number of files processed.
        
    Raises:
        HTTPException: If Azure Files is not configured or sync fails.
    """
    if not azure_files_manager:
        raise HTTPException(
            status_code=400, 
            detail="Azure Files integration not configured. Please set AZURE_STORAGE_CONNECTION_STRING."
        )
    
    try:
        print("Starting Azure Files sync...")
        
        # Get database manager
        db_manager = get_db_manager()
        
        # Sync all PDFs to vector database
        azure_files_manager.sync_all_pdfs_to_vector_db(
            vector_db_manager=db_manager,
            document_processor=extract_text_from_pdf,
            embedding_function=get_embedding
        )
        
        return {"message": "Azure Files sync completed successfully. All PDF files have been processed and added to the vector database."}
        
    except Exception as e:
        print(f"Error during Azure Files sync: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync Azure Files: {e}")

@app.get("/azure_files/list")
async def list_azure_files():
    """
    Endpoint to list all PDF files available in Azure Files.
    
    Returns:
        dict: List of PDF files with their information.
        
    Raises:
        HTTPException: If Azure Files is not configured.
    """
    if not azure_files_manager:
        raise HTTPException(
            status_code=400, 
            detail="Azure Files integration not configured. Please set AZURE_STORAGE_CONNECTION_STRING."
        )
    
    try:
        # Get list of all PDF files
        pdf_files = azure_files_manager.list_pdf_files()
        
        # Get detailed info for each file
        files_info = []
        for file_path in pdf_files:
            file_info = azure_files_manager.get_file_info(file_path)
            if file_info:
                files_info.append(file_info)
        
        return {
            "total_files": len(files_info),
            "files": files_info
        }
        
    except Exception as e:
        print(f"Error listing Azure Files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list Azure Files: {e}")

@app.get("/system/status")
async def get_system_status():
    """
    Endpoint to get system status including Azure Files configuration and uploaded documents.
    
    Returns:
        dict: System status information.
    """
    # Count uploaded documents
    uploaded_docs_count = 0
    if os.path.exists(UPLOAD_FOLDER):
        uploaded_docs_count = len([f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))])
    
    # Count documents in ChromaDB
    db_manager = get_db_manager()
    total_chunks = db_manager.get_document_count()
    
    # Get documents by source
    user_uploads = db_manager.get_documents_by_source("user_upload")
    synced_uploads = db_manager.get_documents_by_source("user_upload_synced")
    azure_files = db_manager.get_documents_by_source("azure_files")
    
    # Count Azure blobs
    azure_blobs_count = 0
    azure_blobs_info = []
    if azure_blob_manager:
        try:
            blobs = azure_blob_manager.list_blobs()
            azure_blobs_count = len(blobs)
            azure_blobs_info = [{"name": blob["name"], "size": blob["size"]} for blob in blobs]
        except Exception as e:
            print(f"Error getting Azure blob info: {e}")
    
    return {
        "status": "running",
        "azure_files_enabled": azure_files_manager is not None,
        "azure_files_share": AZURE_FILES_SHARE_NAME if azure_files_manager else None,
        "azure_blob_enabled": azure_blob_manager is not None,
        "azure_blob_container": AZURE_BLOB_CONTAINER_NAME if azure_blob_manager else None,
        "vector_db_path": CHROMA_DB_PATH,
        "gemini_configured": bool(GEMINI_API_KEY),
        "chromadb": {
            "total_chunks": total_chunks,
            "user_uploads": len(user_uploads),
            "synced_uploads": len(synced_uploads),
            "azure_files": len(azure_files)
        },
        "azure_storage": {
            "blobs_count": azure_blobs_count,
            "blobs": azure_blobs_info
        },
        "uploaded_documents": {
            "count": uploaded_docs_count,
            "storage_path": UPLOAD_FOLDER
        }
    }

@app.get("/debug/chromadb")
async def debug_chromadb():
    """
    Debug endpoint to inspect ChromaDB contents.
    """
    try:
        db_manager = get_db_manager()
        result = db_manager.collection.get()
        
        # Group by source
        sources = {}
        for metadata in result['metadatas']:
            source = metadata.get('source', 'unknown')
            if source not in sources:
                sources[source] = []
            sources[source].append(metadata.get('filename', 'unknown'))
        
        return {
            "total_documents": len(result['documents']),
            "sources": {source: len(files) for source, files in sources.items()},
            "sample_metadata": result['metadatas'][:5] if result['metadatas'] else [],
            "unique_files": {source: list(set(files)) for source, files in sources.items()}
        }
        
    except Exception as e:
        return {"error": str(e)}

