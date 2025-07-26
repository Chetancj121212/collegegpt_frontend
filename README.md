# College Assistant Chatbot

A modern, AI-powered college assistant chatbot built with Next.js and shadcn/ui components. This application provides students and prospective students with instant access to college information through an intuitive chat interface with document upload capabilities.

## ✨ Features

- **Full-screen chat interface** - Gemini-like design for optimal user experience
- **Document upload support** - Upload PDF and PPTX files for AI to learn from
- **Real-time messaging** - Instant responses powered by Google Gemini AI
- **RAG (Retrieval Augmented Generation)** - AI answers based on uploaded documents
- **Dark/Light theme support** - Automatic theme detection and switching
- **Responsive design** - Works seamlessly on desktop and mobile devices
- **Modern UI components** - Built with shadcn/ui for consistent styling
- **Vector database integration** - ChromaDB for efficient document search

## 🚀 Tech Stack

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **UI Components**: shadcn/ui + Radix UI
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **TypeScript**: Full type safety

### Backend
- **Framework**: FastAPI (Python)
- **AI Model**: Google Gemini Pro
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB
- **Document Processing**: pypdf, python-pptx

## 📦 Installation & Setup

### Prerequisites
- Node.js (v18+)
- Python (v3.8+)
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### 1. Frontend Setup

```bash
# Clone the repository
git clone https://github.com/Chetancj121212/collegegpt_frontend.git
cd college_bot

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the frontend
npm run dev
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate
# On macOS/Linux: source .venv/bin/activate

# Install Python dependencies
pip install fastapi uvicorn python-dotenv google-generativeai sentence-transformers chromadb pypdf python-pptx python-multipart

# Create environment file with your Gemini API key
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env

# Start the backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

## 🔧 Configuration

### Environment Variables

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Backend (.env)
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### Gemini API Key Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and add it to your backend `.env` file
4. Replace `your_actual_gemini_api_key_here` with your key

## 🚀 Running the Application

### Method 1: Using Separate Terminals

**Terminal 1 - Backend:**
```bash
cd backend
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

### Method 2: Using VS Code Python Environment

If you're using VS Code, the Python environment will be automatically configured:

1. Open the backend folder in VS Code
2. Select the Python interpreter (`.venv/Scripts/python.exe`)
3. Run the uvicorn command directly

## 📡 API Endpoints

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (FastAPI auto-generated)

### Available Endpoints

- `POST /chat/` - Send chat messages to the AI
- `POST /upload_document/` - Upload PDF or PPTX documents

## 📱 Usage Guide

1. **Starting a conversation**: Type your question in the input field
2. **Sending messages**: Press Enter or click the send button
3. **Multi-line messages**: Use Shift + Enter for new lines
4. **Upload documents**: Click the "Upload Doc" button to add PDF/PPTX files
5. **Document-based Q&A**: Ask questions about uploaded documents
6. **Auto-scroll**: Chat automatically scrolls to the latest message

## 🔄 How RAG Works

1. **Document Upload**: PDF/PPTX files are uploaded and text is extracted
2. **Text Chunking**: Documents are split into manageable chunks
3. **Embedding Generation**: Text chunks are converted to vector embeddings
4. **Storage**: Embeddings are stored in ChromaDB vector database
5. **Query Processing**: User questions are embedded and matched with relevant chunks
6. **Response Generation**: Gemini AI generates responses based on relevant context

## 🛠 Troubleshooting

### Common Issues

1. **Backend Import Errors**
   ```bash
   # Make sure you're in the backend directory
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **CORS Issues**
   - Ensure backend is running on port 8000
   - Check that NEXT_PUBLIC_API_URL is set correctly

3. **API Key Issues**
   - Verify your Gemini API key is valid
   - Check the .env file in the backend directory

4. **File Upload Issues**
   - Ensure backend has write permissions
   - Check supported file types (PDF, PPTX only)

5. **Python Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf .venv  # or rmdir /s .venv on Windows
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 📂 Project Structure

```
college_bot/
├── src/                          # Frontend source code
│   ├── app/
│   │   ├── globals.css          # Global styles
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Main chat interface
│   ├── components/ui/           # shadcn/ui components
│   └── lib/
│       └── utils.ts             # Utility functions
├── backend/                     # Backend source code
│   ├── utils/
│   │   ├── document_processor.py # PDF/PPTX processing
│   │   └── vector_db_manager.py  # ChromaDB operations
│   ├── main.py                  # FastAPI application
│   └── .env                     # Backend environment variables
├── .env.local                   # Frontend environment variables
├── package.json                 # Frontend dependencies
└── README.md                    # This file
```

## 🎨 Customization

### Theme Configuration

The application uses CSS custom properties for theming. Modify `src/app/globals.css` to customize colors:

```css
:root {
  --background: #ffffff;
  --foreground: #171717;
  /* Add more custom variables */
}
```

### UI Components

All UI components are located in `src/components/ui/` and can be customized using the shadcn/ui CLI:

```bash
npx shadcn-ui@latest add [component-name]
```

## 📱 Usage

1. **Starting a conversation**: Type your question in the input field
2. **Sending messages**: Press Enter or click the send button
3. **Multi-line messages**: Use Shift + Enter for new lines
4. **Auto-scroll**: Chat automatically scrolls to the latest message

## 🔮 Future Enhancements

- [ ] User authentication and sessions
- [ ] Chat history persistence
- [ ] Multiple file format support (Word, Excel, etc.)
- [ ] Voice input/output capabilities
- [ ] Multi-language support
- [ ] Admin dashboard for document management
- [ ] Analytics and usage monitoring
- [ ] Custom AI model fine-tuning
- [ ] Real-time collaboration features
- [ ] Mobile app development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript best practices for frontend
- Use proper Python type hints for backend
- Add tests for new features
- Update documentation for new functionality
- Follow existing code style and conventions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/Chetancj121212/collegegpt_frontend/issues) page
2. Review the troubleshooting section above
3. Create a new issue with detailed information
4. Include error logs and system information

## 🏆 Acknowledgments

- **Google Gemini AI** - For providing the language model
- **shadcn/ui** - For the beautiful UI components
- **ChromaDB** - For vector database capabilities
- **FastAPI** - For the robust backend framework
- **Next.js** - For the excellent frontend framework

## 🔗 Useful Links

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Google Gemini AI](https://ai.google.dev/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

---

**Built with ❤️ for educational purposes**
