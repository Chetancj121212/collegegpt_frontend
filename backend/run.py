#!/usr/bin/env python3
"""
Production startup script for the College Bot API.
This script handles environment setup and starts the FastAPI application with memory optimizations.
"""

import os
import gc
import uvicorn

def optimize_memory():
    """Apply memory optimizations."""
    # Set garbage collection thresholds for better memory management
    gc.set_threshold(700, 10, 10)
    
    # Set environment variables for memory optimization
    os.environ["PYTHONOPTIMIZE"] = "2"
    os.environ["PYTHONUNBUFFERED"] = "1"
    
    # Torch/ML optimizations
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"

if __name__ == "__main__":
    # Apply memory optimizations
    optimize_memory()
    
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    
    # Configure uvicorn for production with memory constraints
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        workers=1,  # Single worker to save memory
        loop="asyncio",
        http="httptools"
    )
