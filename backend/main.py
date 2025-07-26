import os
import shutil
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

# Import custom utility modules
from utils.document_processor import extract_text_from_pdf, extract_text_from_pptx, chunk_text
from utils.vector_db_manager import VectorDBManager

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in the .env file.")

# Define folder for uploaded documents (simulates blob storage locally)
UPLOAD_FOLDER = "./uploaded_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Create the directory if it doesn't exist

# Define path for ChromaDB persistence
CHROMA_DB_PATH = "./chroma_db"

# --- Initialize Services ---
app = FastAPI() # Create FastAPI application instance

# Configure Google Generative AI (Gemini) with the API key
genai.configure(api_key=GEMINI_API_KEY)
# Initialize the Gemini model for text generation
gemini_model = genai.GenerativeModel('gemini-1.5-flash')
# Initialize the Sentence Transformer model for embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
# Initialize the VectorDBManager for ChromaDB operations
db_manager = VectorDBManager(db_path=CHROMA_DB_PATH)

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
    using the Sentence Transformer model.

    Args:
        text (str): The input text to embed.

    Returns:
        list[float]: A list of floats representing the text embedding.
    """
    return embedding_model.encode(text).tolist()

# --- API Endpoints ---

@app.post("/upload_document/")
async def upload_document(file: UploadFile = File(...)):
    """
    Endpoint to upload a document (PDF or PPTX), extract its text,
    chunk the text, generate embeddings, and store them in the vector database.

    Args:
        file (UploadFile): The uploaded file object from the request.

    Returns:
        dict: A message indicating the success of the operation.

    Raises:
        HTTPException: If the file type is unsupported, text extraction fails,
                       chunking fails, or any other processing error occurs.
    """
    # Define the full path where the uploaded file will be saved temporarily
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        # Save the uploaded file to the local UPLOAD_FOLDER
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document_text = ""
        # Determine file type and extract text accordingly
        if file.filename.endswith(".pdf"):
            document_text = extract_text_from_pdf(file_location)
        elif file.filename.endswith(".pptx"):
            document_text = extract_text_from_pptx(file_location)
        else:
            # Raise an error for unsupported file types
            raise HTTPException(status_code=400, detail="Unsupported file type. Only PDF and PPTX are supported.")

        if not document_text:
            # Raise an error if no text could be extracted
            raise HTTPException(status_code=500, detail="Could not extract text from the document.")

        # Chunk the extracted text
        chunks = chunk_text(document_text)
        if not chunks:
            # Raise an error if chunking results in no chunks
            raise HTTPException(status_code=500, detail="Could not chunk the document text.")

        # Generate embeddings for each text chunk
        embeddings = [get_embedding(chunk) for chunk in chunks]
        # Create metadata for each chunk (filename and chunk index)
        metadatas = [{"filename": file.filename, "chunk_index": i} for i, _ in enumerate(chunks)]

        # Add the chunks, embeddings, and metadata to ChromaDB
        db_manager.add_documents(chunks, embeddings, metadatas)

        return {"message": f"Document '{file.filename}' processed and added to vector DB successfully."}
    except HTTPException as e:
        # Re-raise HTTPExceptions as they are already formatted for FastAPI
        raise e
    except Exception as e:
        # Catch any other unexpected errors and return a generic 500 error
        print(f"Error during document upload and processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")
    finally:
        # Clean up: remove the temporarily saved file after processing
        if os.path.exists(file_location):
            os.remove(file_location)

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
            print(f"Relevant chunks found. Prompt sent to Gemini:\n{prompt}")

        # Call the Gemini model to generate a response
        response = gemini_model.generate_content(prompt)
        # Return the generated text response
        return {"response": response.text}
    except Exception as e:
        # Catch any errors during chat processing and return a 500 error
        print(f"Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get response: {e}")

