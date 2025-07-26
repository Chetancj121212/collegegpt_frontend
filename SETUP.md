# College Assistant - Setup Instructions

## Prerequisites

Make sure you have the following installed:
- Node.js (v18+)
- Python (v3.8+)
- pip (Python package manager)

## Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn python-dotenv google-generativeai sentence-transformers chromadb python-pptx pypdf2 python-multipart
   ```

4. **Create a .env file in the backend directory:**
   ```bash
   # Create .env file with your Gemini API key
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the FastAPI backend:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Frontend Setup

1. **Navigate to the frontend directory (project root):**
   ```bash
   cd ../  # if you're in the backend folder
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Run the Next.js frontend:**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

## Running Both Services

1. **Terminal 1 - Backend:**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Terminal 2 - Frontend:**
   ```bash
   npm run dev
   ```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs (FastAPI auto-generated documentation)

## Features

✅ **Chat Interface**: Ask questions about college-related topics
✅ **Document Upload**: Upload PDF or PPTX files for the AI to learn from
✅ **Real-time Responses**: Get instant responses powered by Google Gemini
✅ **Vector Database**: ChromaDB for efficient document search and retrieval
✅ **RAG (Retrieval Augmented Generation)**: AI answers based on uploaded documents

## Troubleshooting

1. **CORS Issues**: Make sure the backend is running on port 8000
2. **API Key Issues**: Ensure your Gemini API key is set in the backend .env file
3. **File Upload Issues**: Check that the backend has write permissions for the upload directories
4. **Dependencies**: Make sure all dependencies are installed in both frontend and backend

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
GEMINI_API_KEY=your_gemini_api_key_here
```
