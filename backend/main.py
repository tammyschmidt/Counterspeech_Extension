# FastAPI app entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import api
from config import CORS_ORIGINS, CORS_ORIGIN_REGEX
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Counter Speech API",
    description="API for generating counter speech suggestions against hate speech",
    version="1.0.0"
)

# Configure CORS for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Counter Speech API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    
    logger.info(f"Starting Counter Speech API on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )

