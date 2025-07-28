# College Assistant - AI-Powered Document Q&A System

A full-stack RAG (Retrieval-Augmented Generation) application that allows users to chat with their documents using AI. The system features a modern Next.js frontend and a robust FastAPI backend with vector database integration.

## 🚀 Live Demo

- **Frontend**: [Deployed on Vercel/Railway](https://your-frontend-url.com)
- **Backend API**: [Railway Deployment](https://your-backend-url.railway.app)
- **API Docs**: [FastAPI Documentation](https://your-backend-url.railway.app/docs)

## 🚀 Features

- **🔄 Real-time Chat Interface**: Modern chat UI with typing indicators and auto-scroll
- **📁 Document Upload & Processing**: Support for PDF and PPTX files with automatic text extraction
- **🔍 Intelligent Document Search**: Vector-based similarity search using ChromaDB
- **🤖 AI-Powered Responses**: Google Gemini integration for intelligent, context-aware answers
- **☁️ Azure Cloud Integration**:
  - Azure Blob Storage for uploaded documents
  - Azure Files for existing document collections
- **⚡ Memory Optimization**: Lazy loading of models and automatic memory management
- **📱 Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **🔒 Type Safety**: Full TypeScript support across the frontend
- **🌐 Production Ready**: Deployed on Railway with automatic CI/CD

## 🏗️ Tech Stack

### Frontend

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components using Radix UI primitives
  - Button, Input, Card, ScrollArea, etc.
- **Icons**: Lucide React
- **State Management**: React Hooks (useState, useRef, useEffect)
- **HTTP Client**: Native Fetch API

### Backend

- **Framework**: FastAPI (Python)
- **Language**: Python 3.11+ (3.13 recommended)
- **AI/ML Stack**:
  - Google Gemini API for text generation
  - Google Generative AI for embeddings
  - Sentence Transformers for document vectorization
- **Vector Database**: ChromaDB for storing and querying document embeddings
- **Document Processing**:
  - PyPDF for PDF text extraction (updated from PyPDF2)
  - python-pptx for PowerPoint processing
- **File Handling**: FastAPI's UploadFile with multipart form support
- **Deployment**: Railway, Render, or Docker-compatible platforms

### Cloud Services

- **Azure Blob Storage**: Document storage and management
- **Azure Files**: Integration with existing document repositories
- **Google AI Platform**: Gemini API for natural language processing

### Development Tools

- **Package Management**: npm/yarn (frontend), pip (backend)
- **Build System**: Next.js built-in bundler
- **Environment**: Hot reload for both frontend and backend

## 🏛️ Architecture

```
┌─────────────────┐    HTTP/REST     ┌─────────────────┐
│   Next.js App   │ ───────────────► │  FastAPI Server │
│   (Frontend)    │                  │   (Backend)     │
└─────────────────┘                  └─────────────────┘
                                              │
                                              ▼
┌─────────────────┐                  ┌─────────────────┐
│  Google Gemini  │ ◄────────────────┤   ChromaDB      │
│      API        │                  │ (Vector Store)  │
└─────────────────┘                  └─────────────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │ Azure Storage   │
                                     │ (Blob + Files)  │
                                     └─────────────────┘
```

## 📋 Prerequisites

- **Node.js** 18+ and npm/yarn (for frontend)
- **Python** 3.11+ (3.13 recommended for optimal performance)
- **Google Gemini API key** (required - get from [Google AI Studio](https://makersuite.google.com/app/apikey))
- **Azure Storage Account** (optional but recommended for production)
- **Git** for version control

## 🚀 Quick Start

### Method 1: Railway Deployment (Recommended for Production)

1. **Fork this repository**
2. **Connect to Railway**:
   - Visit [Railway](https://railway.app)
   - Connect your GitHub account
   - Deploy this repository
3. **Set environment variables** in Railway dashboard:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
   AZURE_FILES_SHARE_NAME=containerclggpt
   AZURE_BLOB_CONNECTION_STRING=your_azure_blob_connection_string
   AZURE_BLOB_CONTAINER_NAME=uploaded-documents
   ```

### Method 2: Local Development

### Backend Setup

1. **Navigate to backend directory**

   ```bash
   cd backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the `backend` directory:

   ```env
   # Required
   GEMINI_API_KEY=your_gemini_api_key_here

   # Optional - Azure Blob Storage
   AZURE_BLOB_CONNECTION_STRING=your_azure_blob_connection_string
   AZURE_BLOB_CONTAINER_NAME=uploaded-documents

   # Optional - Azure Files
   AZURE_STORAGE_CONNECTION_STRING=your_azure_files_connection_string
   AZURE_FILES_SHARE_NAME=college-documents
   ```

5. **Start the backend server**
   ```bash
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to project root and install dependencies**

   ```bash
   npm install
   # or
   yarn install
   ```

2. **Configure environment variables**
   Create a `.env.local` file in the root directory:

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Start the development server**

   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Access the application**
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`

## 📁 Project Structure

```
college_bot/
├── 📁 frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Main chat interface
│   │   │   ├── layout.tsx            # App layout
│   │   │   └── globals.css           # Global styles
│   │   ├── components/
│   │   │   └── ui/                   # Reusable UI components
│   │   └── lib/
│   │       └── utils.ts              # Utility functions
│   ├── package.json                  # Frontend dependencies
│   └── tailwind.config.js           # Tailwind configuration
├── 📁 backend/
│   ├── main.py                      # FastAPI application
│   ├── config.py                    # Configuration settings
│   ├── requirements.txt             # Python dependencies
│   ├── utils/
│   │   ├── document_processor.py    # Text extraction & chunking
│   │   ├── vector_db_manager.py     # ChromaDB operations
│   │   ├── azure_files_manager.py   # Azure Files integration
│   │   └── azure_blob_manager.py    # Azure Blob integration
│   ├── uploaded_docs/               # Local document storage
│   └── chroma_db/                   # ChromaDB persistence
├── README.md                        # This file
├── next.config.ts                   # Next.js configuration
└── tsconfig.json                    # TypeScript configuration
```

## 🔌 API Endpoints

### 💬 Chat Endpoints

- `POST /chat/` - Chat with JSON input (ChatRequest model)
- `POST /chat_simple/` - Chat with form data input
- Both endpoints support RAG-based responses using uploaded documents

### 📄 Document Management

- `POST /upload_document/` - Upload and process PDF/PPTX files
- `GET /uploaded_documents/` - List all uploaded documents
- `DELETE /uploaded_documents/{filename}` - Delete specific document

### ☁️ Azure Integration

- `POST /sync_azure_blobs/` - Sync Azure Blob Storage documents
- `POST /sync_azure_files/` - Sync Azure Files documents
- `GET /azure_files/list` - List Azure Files documents

### 🔧 System & Health

- `GET /` - Root endpoint with API status
- `GET /health` - Health check with system status
- `POST /memory/cleanup` - Force memory cleanup
- `GET /system/status` - Complete system status
- `GET /debug/chromadb` - Debug ChromaDB contents

## 🔄 Document Processing Pipeline

1. **📤 Upload**: User uploads document via frontend interface
2. **💾 Storage**: Document stored in Azure Blob (or locally as fallback)
3. **📝 Text Extraction**: Extract text content from PDF/PPTX files
4. **✂️ Chunking**: Split text into manageable, overlapping chunks
5. **🧮 Embedding**: Generate vector embeddings using Google's embedding model
6. **🗄️ Storage**: Store embeddings and metadata in ChromaDB
7. **🔍 Indexing**: Ready for similarity search and retrieval

## 💬 Chat Flow

1. **❓ Query**: User types question in the chat interface
2. **🔄 Processing**: Frontend sends query to `/chat_simple/` endpoint
3. **🧮 Embedding**: Backend generates embedding for user query
4. **🔍 Retrieval**: ChromaDB performs similarity search for relevant chunks
5. **🤖 Generation**: Google Gemini generates response using retrieved context
6. **📤 Response**: AI-generated answer displayed in chat interface
7. **📊 Metadata**: Include sources and confidence information

## ⚙️ Configuration

### Backend Configuration (`config.py`)

- `EMBEDDING_MODEL_NAME`: Model for generating document embeddings
- `EMBEDDING_BATCH_SIZE`: Batch size for processing embeddings
- `MAX_CHUNKS_PER_DOCUMENT`: Maximum chunks per document (memory management)
- `MEMORY_WARNING_THRESHOLD`: Memory usage warning threshold
- `MEMORY_CRITICAL_THRESHOLD`: Critical memory usage threshold

### Frontend Configuration

- `NEXT_PUBLIC_API_URL`: Backend API base URL
- Tailwind CSS for styling configuration
- TypeScript strict mode enabled

## 🛠️ Development

### Frontend Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Backend Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start with auto-reload
uvicorn main:app --reload

# Run with specific host/port
python main.py
```

### Adding New Features

1. **New File Types**: Extend `document_processor.py` with new extractors
2. **UI Components**: Add components to `src/components/ui/`
3. **API Endpoints**: Add new routes in `main.py`
4. **Azure Services**: Extend manager classes in `utils/`

## 🔍 Troubleshooting

### Common Frontend Issues

- **API Connection**: Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- **CORS Errors**: Check backend CORS configuration
- **Build Errors**: Ensure TypeScript types are correct

### Common Backend Issues

- **Memory Issues**: Use `/memory/cleanup` endpoint or reduce batch sizes
- **Azure Connection**: Verify connection strings and network access
- **Model Loading**: Ensure sufficient disk space for model downloads
- **ChromaDB Issues**: Check database permissions and storage path
- **Railway Deployment**:
  - Check build logs for dependency installation errors
  - Verify environment variables are set correctly
  - Ensure Python version compatibility (3.11+ recommended)
  - Monitor memory usage during deployment

### Debugging Tools

- Frontend: Browser DevTools, React DevTools
- Backend: FastAPI automatic docs at `/docs`
- System: Use `/debug/chromadb` and `/system/status` endpoints

## 🚀 Deployment

### Railway Deployment (Backend)

1. **Automatic Deployment**:

   - Railway automatically detects Python projects
   - Uses `render.yaml` configuration for deployment settings
   - Installs dependencies from `requirements.txt`

2. **Manual Configuration**:

   ```yaml
   # render.yaml (already configured)
   services:
     - type: web
       name: college-bot-backend
       runtime: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment Variables** (set in Railway dashboard):
   ```env
   GEMINI_API_KEY=your_production_gemini_key
   AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
   AZURE_FILES_SHARE_NAME=containerclggpt
   AZURE_BLOB_CONNECTION_STRING=your_azure_blob_connection_string
   AZURE_BLOB_CONTAINER_NAME=uploaded-documents
   ```

### Frontend Deployment (Vercel/Netlify)

1. **Vercel Deployment**:

   ```bash
   npm run build
   # Deploy the .next folder to Vercel
   ```

2. **Environment Variables**:
   ```env
   NEXT_PUBLIC_API_URL=https://your-railway-backend-url.railway.app
   ```

### Docker Deployment (Alternative)

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Deployment Troubleshooting

**Common Railway Issues**:

- Memory limits: Use memory optimization settings
- Build timeouts: Ensure requirements.txt is optimized
- Port binding: Railway automatically sets $PORT environment variable

**Environment Variables for Production**:

```env
# Frontend
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app

# Backend (Railway)
GEMINI_API_KEY=your_production_key
AZURE_BLOB_CONNECTION_STRING=your_production_string
CORS_ORIGINS=https://your-frontend-url.com
PORT=8000  # Railway sets this automatically
```

## 📊 Performance Optimization

- **Frontend**: Next.js automatic code splitting and optimization
- **Backend**: Lazy loading of AI models and batch processing
- **Database**: ChromaDB efficient vector similarity search
- **Memory**: Automatic cleanup and configurable batch sizes
- **Azure**: CDN integration for document delivery

## 🔒 Security Best Practices

- Store API keys in environment variables, never in code
- Configure CORS origins for production deployment
- Use Azure managed identities when possible
- Implement rate limiting for production APIs
- Validate file uploads and sanitize inputs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: Create an issue on GitHub
- **API Documentation**: Visit `/docs` when backend is running
- **System Status**: Check `/system/status` endpoint
- **Debug Info**: Use `/debug/chromadb` for database insights

## 🔮 Future Enhancements

- [ ] WebSocket support for real-time chat
- [ ] Multi-language document support
- [ ] Advanced search filters and sorting
- [ ] User authentication and document permissions
- [ ] Conversation history and memory
- [ ] Mobile app using React Native
- [ ] Advanced analytics and usage tracking
- [ ] Improved Railway deployment optimization
- [ ] Auto-scaling based on usage patterns

---

## 📊 Current Status

**Deployment Status**:

- ✅ Backend: Railway deployment configured
- ✅ Frontend: Next.js application ready
- ✅ Database: ChromaDB integration
- ✅ AI: Google Gemini API integration
- ✅ Storage: Azure Blob & Files support

**Last Updated**: July 29, 2025
