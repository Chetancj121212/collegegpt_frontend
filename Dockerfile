FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Create necessary directories
RUN mkdir -p uploaded_docs chroma_db

# Expose port
EXPOSE 8000

# Start command using startup script
CMD ["./start.sh"]
