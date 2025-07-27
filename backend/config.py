# Memory optimization settings for Render deployment

# ChromaDB settings
CHROMA_DB_SETTINGS = {
    "anonymized_telemetry": False,
    "allow_reset": True,
    "persist_directory": "./chroma_db"
}

# Embedding batch settings
EMBEDDING_BATCH_SIZE = 2  # Process only 2 chunks at a time
MAX_CHUNKS_PER_DOCUMENT = 20  # Limit chunks per document

# Memory thresholds (in MB)
MEMORY_WARNING_THRESHOLD = 400  # 400MB warning
MEMORY_CRITICAL_THRESHOLD = 480  # 480MB critical (close to 512MB limit)

# Sentence transformer model settings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # ~90MB instead of larger models
EMBEDDING_DEVICE = "cpu"  # Force CPU usage to save memory

# Text chunking settings for smaller chunks
CHUNK_SIZE = 500  # Smaller chunks
CHUNK_OVERLAP = 50
