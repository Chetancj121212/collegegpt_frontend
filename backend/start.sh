#!/bin/bash

# Create necessary directories
mkdir -p uploaded_docs
mkdir -p chroma_db

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}