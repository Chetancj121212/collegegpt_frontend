import os
import tempfile
import gc
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from pydantic import BaseModel

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
        print(f"✅ Loaded embedding model: {EMBEDDING_MODEL_NAME}")
    return embedding_model

def get_gemini_model():
    """Lazy load the Gemini model."""
    global gemini_model
    if gemini_model is None:
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Loaded Gemini model")
    return gemini_model

def get_db_manager():
    """Lazy load the database manager."""
    global db_manager
    if db_manager is None:
        db_manager = VectorDBManager(db_path=CHROMA_DB_PATH)
        print("✅ Loaded ChromaDB manager")
    return db_manager

def clear_models():
    """Clear all models from memory."""
    global embedding_model, gemini_model
    models_cleared = []
    
    if embedding_model is not None:
        embedding_model = None
        models_cleared.append("embedding_model")
    
    if gemini_model is not None:
        gemini_model = None
        models_cleared.append("gemini_model")
    
    gc.collect()
    return models_cleared

# Initialize Azure managers (lightweight)
azure_files_manager = None
if AZURE_STORAGE_CONNECTION_STRING:
    try:
        azure_files_manager = AzureFilesManager(
            connection_string=AZURE_STORAGE_CONNECTION_STRING,
            share_name=AZURE_FILES_SHARE_NAME
        )
        print(f"✅ Azure Files enabled: {AZURE_FILES_SHARE_NAME}")
    except Exception as e:
        print(f"⚠️ Azure Files failed: {e}")

azure_blob_manager = None
if AZURE_BLOB_CONNECTION_STRING:
    try:
        azure_blob_manager = AzureBlobManager(
            connection_string=AZURE_BLOB_CONNECTION_STRING,
            container_name=AZURE_BLOB_CONTAINER_NAME
        )
        print(f"✅ Azure Blob enabled: {AZURE_BLOB_CONTAINER_NAME}")
    except Exception as e:
        print(f"⚠️ Azure Blob failed: {e}")

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
    try:
        model = get_embedding_model()
        # Truncate text if too long to save memory
        if len(text) > 512:
            text = text[:512]
        
        embedding = model.encode(text, show_progress_bar=False).tolist()
        
        # Force garbage collection after each embedding
        gc.collect()
        return embedding
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        # Clear models on error to free memory
        clear_models()
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

# --- API Endpoints ---

@app.get("/")
async def root():
    """
    Root endpoint to verify the API is running.
    """
    return {
        "message": "College Bot API - Memory Optimized",
        "status": "healthy",
        "memory_limit": "512MB"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "models_loaded": {
            "embedding_model": embedding_model is not None,
            "gemini_model": gemini_model is not None,
            "db_manager": db_manager is not None
        },
        "azure_enabled": {
            "files": azure_files_manager is not None,
            "blob": azure_blob_manager is not None
        },
        "memory_optimization": "enabled"
    }

@app.post("/memory/cleanup")
async def cleanup_memory():
    """
    Endpoint to force garbage collection and clear unused models.
    """
    models_cleared = clear_models()
    
    return {
        "message": "Memory cleanup completed",
        "models_cleared": models_cleared
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
    
    try:
        # Clear models before processing to free memory
        clear_models()
        
        # Read file
        file_content = await file.read()
        
        # Use local storage to minimize memory usage
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_location, "wb") as buffer:
            buffer.write(file_content)
        temp_file_path = file_location
        
        # Extract text
        print(f"🔄 Extracting text from: {file.filename}")
        if file.filename.endswith(".pdf"):
            document_text = extract_text_from_pdf(temp_file_path)
        else:
            document_text = extract_text_from_pptx(temp_file_path)
        
        if not document_text:
            raise HTTPException(status_code=500, detail="Could not extract text")
        
        # Chunk text with smaller chunks
        print(f"🔄 Chunking text (max {MAX_CHUNKS_PER_DOCUMENT} chunks)")
        chunks = chunk_text(document_text)
        
        # Limit chunks aggressively
        if len(chunks) > MAX_CHUNKS_PER_DOCUMENT:
            chunks = chunks[:MAX_CHUNKS_PER_DOCUMENT]
        
        if not chunks:
            raise HTTPException(status_code=500, detail="Could not chunk text")
        
        # Generate embeddings with very small batches
        print(f"🔄 Generating embeddings for {len(chunks)} chunks")
        embeddings = []
        
        for i, chunk in enumerate(chunks):
            try:
                embedding = get_embedding(chunk)
                embeddings.append(embedding)
                
                # Clear models every few embeddings to free memory
                if (i + 1) % 5 == 0:
                    clear_models()
                
                print(f"   - Processed chunk {i + 1}/{len(chunks)}")
                
            except Exception as e:
                print(f"❌ Failed to process chunk {i + 1}: {e}")
                # Continue with remaining chunks
                continue
        
        if not embeddings:
            raise HTTPException(status_code=500, detail="Failed to generate embeddings")
        
        # Create metadata
        metadatas = [
            {
                "filename": file.filename,
                "chunk_index": i,
                "source": "user_upload",
                "storage_location": f"Local: {file_location}"
            }
            for i in range(len(embeddings))
        ]
        
        # Add to database
        print(f"🔄 Adding {len(embeddings)} chunks to ChromaDB")
        db_manager = get_db_manager()
        
        # Use only the chunks that have embeddings
        valid_chunks = chunks[:len(embeddings)]
        db_manager.add_documents(valid_chunks, embeddings, metadatas)
        
        # Final cleanup
        clear_models()
        
        return {
            "message": f"Document '{file.filename}' processed successfully",
            "details": {
                "filename": file.filename,
                "chunks_processed": len(embeddings),
                "storage_type": "Local Storage"
            }
        }
        
    except Exception as e:
        # Cleanup on error
        clear_models()
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

class ChatRequest(BaseModel):
    user_query: str

@app.post("/chat/")
async def chat(request: ChatRequest):
    """
    Memory-optimized chat endpoint with JSON input.
    """
    print(f"Received request: {request}")
    print(f"User query: {request.user_query}")
    
    if not request.user_query or not request.user_query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Clear models before processing
        clear_models()
        
        # Get relevant documents
        db_manager = get_db_manager()
        query_embedding = get_embedding(request.user_query)
        
        # Search for relevant chunks
        results = db_manager.similarity_search(query_embedding, top_k=3)
        
        if not results:
            return {
                "response": "I don't have enough information to answer your question based on the uploaded documents. Please upload relevant documents first.",
                "sources": [],
                "context_found": False
            }
        
        # Prepare context - limit context length to save memory
        context_parts = []
        for doc in results:
            content = doc.get("content", "")
            if len(content) > 500:  # Truncate long content
                content = content[:500] + "..."
            context_parts.append(content)
        
        context = "\n\n".join(context_parts)
        
        # Generate response
        gemini_model = get_gemini_model()
        
        prompt = f"""Based on the following context from college documents, answer the user's question:

Context:
{context}

Question: {request.user_query}

Please provide a helpful and accurate answer based on the context. If the context doesn't contain enough information to fully answer the question, mention that and provide what information is available.

Answer:"""
        
        response = gemini_model.generate_content(prompt)
        
        # Clear models after use
        clear_models()
        
        return {
            "response": response.text,
            "sources": list(set([doc["metadata"]["filename"] for doc in results if "metadata" in doc and "filename" in doc["metadata"]])),
            "context_found": True,
            "chunks_used": len(results)
        }
        
    except Exception as e:
        clear_models()
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# Add a simple test endpoint
@app.post("/chat_simple/")
async def chat_simple(query: str = Form(...)):
    """
    Simple chat endpoint for testing with form data.
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Clear models before processing
        clear_models()
        
        # Get relevant documents
        db_manager = get_db_manager()
        query_embedding = get_embedding(query)
        
        # Search for relevant chunks
        results = db_manager.similarity_search(query_embedding, top_k=3)
        
        if not results:
            return {
                "response": "I don't have enough information to answer your question based on the uploaded documents. Please upload relevant documents first.",
                "sources": [],
                "context_found": False
            }
        
        # Prepare context - limit context length to save memory
        context_parts = []
        for doc in results:
            content = doc.get("content", "")
            if len(content) > 500:  # Truncate long content
                content = content[:500] + "..."
            context_parts.append(content)
        
        context = "\n\n".join(context_parts)
        
        # Generate response
        gemini_model = get_gemini_model()
        
        prompt = f"""Based on the following context from college documents, answer the user's question:

Context:
{context}

Question: {query}

Please provide a helpful and accurate answer based on the context.

Answer:"""
        
        response = gemini_model.generate_content(prompt)
        
        # Clear models after use
        clear_models()
        
        return {
            "response": response.text,
            "sources": list(set([doc["metadata"]["filename"] for doc in results if "metadata" in doc and "filename" in doc["metadata"]])),
            "context_found": True,
            "chunks_used": len(results)
        }
        
    except Exception as e:
        clear_models()
        print(f"Chat simple error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# Additional endpoints that might be missing
@app.get("/uploaded_documents/")
async def list_uploaded_documents():
    """List all uploaded documents."""
    try:
        if os.path.exists(UPLOAD_FOLDER):
            files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(('.pdf', '.pptx'))]
            return {"documents": files, "count": len(files)}
        else:
            return {"documents": [], "count": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.delete("/uploaded_documents/{filename}")
async def delete_document(filename: str):
    """Delete a specific document."""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": f"Document '{filename}' deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.get("/debug/chromadb")
async def debug_chromadb():
    """Debug ChromaDB contents."""
    try:
        db_manager = get_db_manager()
        collection = db_manager.collection
        
        # Get collection info
        count = collection.count()
        
        if count > 0:
            # Get a few sample documents
            results = collection.get(limit=5)
            return {
                "total_documents": count,
                "sample_documents": {
                    "ids": results.get("ids", []),
                    "metadatas": results.get("metadatas", [])
                }
            }
        else:
            return {
                "total_documents": 0,
                "message": "No documents in database"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")

# If you're running this file directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

