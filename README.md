# College Bot - AI-Powered Document Q&A System

A FastAPI-based chatbot that uses RAG (Retrieval-Augmented Generation) to answer questions based on uploaded documents. The system supports PDF and PPTX files, uses ChromaDB for vector storage, and integrates with Azure services for scalable document storage.

## Features

- **Document Upload & Processing**: Upload PDF and PPTX files with automatic text extraction and chunking
- **Vector Database**: ChromaDB for efficient similarity search and document retrieval
- **AI-Powered Chat**: Google Gemini integration for intelligent responses
- **Azure Integration**: 
  - Azure Blob Storage for uploaded documents
  - Azure Files for existing document collections
- **Memory Optimization**: Lazy loading of models and memory management endpoints
- **RESTful API**: Complete FastAPI backend with CORS support

## Architecture

```
Frontend (React/HTML) → FastAPI Backend → ChromaDB (Vector DB)
                                     ↓
                              Google Gemini API
                                     ↓
                              Azure Storage Services
```

## Prerequisites

- Python 3.8+
- Google Gemini API key
- Azure Storage Account (optional but recommended)
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd college_bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the `backend` directory:
   ```env
   # Required
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Optional - Azure Blob Storage (for uploaded documents)
   AZURE_BLOB_CONNECTION_STRING=your_azure_blob_connection_string
   AZURE_BLOB_CONTAINER_NAME=uploaded-documents
   
   # Optional - Azure Files (for existing document collections)
   AZURE_STORAGE_CONNECTION_STRING=your_azure_files_connection_string
   AZURE_FILES_SHARE_NAME=college-documents
   ```

## Configuration

The application uses several configuration parameters defined in `config.py`:

- `EMBEDDING_MODEL_NAME`: Sentence transformer model for embeddings
- `EMBEDDING_BATCH_SIZE`: Batch size for processing embeddings
- `MAX_CHUNKS_PER_DOCUMENT`: Maximum chunks per document to manage memory
- `MEMORY_WARNING_THRESHOLD`: Memory usage warning threshold
- `MEMORY_CRITICAL_THRESHOLD`: Critical memory usage threshold

## Usage

1. **Start the backend server**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Health Check: `http://localhost:8000/health`
   - API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with API status
- `GET /health` - Health check with system status
- `POST /upload_document/` - Upload and process documents
- `POST /chat/` - Chat with the AI using uploaded documents
- `POST /memory/cleanup` - Force memory cleanup

### Document Management

- `GET /uploaded_documents/` - List all uploaded documents
- `DELETE /uploaded_documents/{filename}` - Delete a specific document
- `POST /sync_azure_blobs/` - Sync Azure Blob Storage documents
- `POST /sync_azure_files/` - Sync Azure Files documents

### System Status

- `GET /system/status` - Complete system status
- `GET /azure_files/list` - List Azure Files documents
- `GET /debug/chromadb` - Debug ChromaDB contents

## Document Processing Pipeline

1. **Upload**: Document uploaded via `/upload_document/`
2. **Storage**: Stored in Azure Blob (or locally as fallback)
3. **Text Extraction**: Extract text from PDF/PPTX
4. **Chunking**: Split text into manageable chunks
5. **Embedding**: Generate vector embeddings using Sentence Transformers
6. **Storage**: Store embeddings and metadata in ChromaDB

## Chat Flow

1. **Query**: User sends question via `/chat/`
2. **Embedding**: Generate embedding for user query
3. **Retrieval**: Find relevant document chunks using similarity search
4. **Generation**: Generate response using Google Gemini with retrieved context
5. **Response**: Return AI-generated answer to user

## Memory Management

The application includes several memory optimization features:

- **Lazy Loading**: Models loaded only when needed
- **Batch Processing**: Embeddings processed in configurable batches
- **Garbage Collection**: Automatic cleanup after operations
- **Memory Cleanup Endpoint**: Manual memory management via API

## Azure Integration

### Azure Blob Storage
- Stores uploaded documents with automatic retry mechanism
- Supports document synchronization to vector database
- Fallback to local storage if Azure is unavailable

### Azure Files
- Integration with existing document collections
- Bulk PDF processing and synchronization
- Support for large document repositories

## Error Handling

- Comprehensive error handling with detailed HTTP responses
- Automatic cleanup of temporary files
- Retry mechanisms for Azure operations
- Graceful fallback to local storage

## Development

### Project Structure
```
college_bot/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── requirements.txt     # Python dependencies
│   ├── utils/
│   │   ├── document_processor.py    # Text extraction
│   │   ├── vector_db_manager.py     # ChromaDB operations
│   │   ├── azure_files_manager.py   # Azure Files integration
│   │   └── azure_blob_manager.py    # Azure Blob integration
│   ├── uploaded_docs/       # Local document storage
│   └── chroma_db/          # ChromaDB persistence
└── frontend/               # Frontend application (if applicable)
```

### Adding New Features

1. Document processors for new file types in `utils/document_processor.py`
2. New API endpoints in `main.py`
3. Additional Azure services in respective manager files
4. Configuration updates in `config.py`

## Troubleshooting

### Common Issues

1. **Memory Issues**: Use memory cleanup endpoint or reduce batch sizes
2. **Azure Connection**: Check connection strings and network connectivity
3. **Model Loading**: Ensure sufficient disk space for model downloads
4. **CORS Issues**: Verify CORS configuration for frontend integration

### Logs and Debugging

- Enable debug logging by setting log level in the application
- Use `/debug/chromadb` endpoint to inspect vector database
- Check `/system/status` for overall system health

## Performance Optimization

- Use smaller embedding models for faster processing
- Adjust batch sizes based on available memory
- Consider using Azure services for better scalability
- Implement caching for frequently accessed documents

## Security Considerations

- Store API keys securely in environment variables
- Restrict CORS origins in production
- Use Azure managed identities when possible
- Implement rate limiting for production deployments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Submit a pull request with detailed description

## License

[Add your license information here]

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review system status at `/system/status`
- Use debug endpoints for troubleshooting
