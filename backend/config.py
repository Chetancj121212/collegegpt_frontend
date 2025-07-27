# Memory optimization settings for Render deployment

# ChromaDB settings
CHROMA_DB_SETTINGS = {
    "anonymized_telemetry": False,
    "allow_reset": True,
    "persist_directory": "./chroma_db"
}

# Embedding batch settings
EMBEDDING_BATCH_SIZE = 3  # Smaller batches for memory efficiency
MAX_CHUNKS_PER_DOCUMENT = 50  # Limit chunks per document

# Memory thresholds (in MB)
MEMORY_WARNING_THRESHOLD = 400  # Warning at 400MB
MEMORY_CRITICAL_THRESHOLD = 480  # Critical at 480MB

# Sentence transformer model settings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # Smallest efficient model
EMBEDDING_DEVICE = "cpu"  # Force CPU usage to save memory
