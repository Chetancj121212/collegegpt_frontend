#!/usr/bin/env python3
"""
Production startup script for the College Bot API.
This script handles environment setup and starts the FastAPI application.
"""

import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    
    # Configure uvicorn for production
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
