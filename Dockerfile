# Use slim Python image and optimize for size
FROM python:3.11-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Set pip configurations for faster installs
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy minimal requirements
COPY backend/requirements-minimal.txt requirements.txt

# Install PyTorch CPU-only first (much smaller than CUDA version)
RUN pip install torch==2.7.1+cpu torchvision==0.22.1+cpu --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install -r requirements.txt

# Clean up to reduce image size
RUN apt-get remove -y gcc g++ && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache

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
