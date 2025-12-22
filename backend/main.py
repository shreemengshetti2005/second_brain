"""
Main FastAPI application.
Entry point for the Second Brain Agent backend.
"""

import sys
import os

# Add parent directory to path - MUST BE FIRST
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.database import init_db, check_db_connection
from backend.api import notes, query, insights, telegram_webhook, gdrive, users
from backend.utils.google_api_utils import validate_all_google_apis

# ... rest of the file stays the same

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("="*50)
    logger.info("🚀 Starting Second Brain Agent API")
    logger.info("="*50)
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        init_db()
        
        if check_db_connection():
            logger.info("✅ Database connection successful")
        else:
            logger.error("❌ Database connection failed")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
    
    # Validate Google APIs
    try:
        logger.info("Validating Google API configurations...")
        api_status = validate_all_google_apis()
        
        for api_name, is_valid in api_status.items():
            status = "✅" if is_valid else "⚠️"
            logger.info(f"{status} {api_name}: {'Configured' if is_valid else 'Not configured'}")
    except Exception as e:
        logger.error(f"Error validating APIs: {e}")
    
    logger.info("="*50)
    logger.info(f"🌐 API running at: http://localhost:8000")
    logger.info(f"📚 API docs at: http://localhost:8000/docs")
    logger.info("="*50)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Second Brain Agent API...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered voice and text note-taking system with Google Cloud integration",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint with service status.
    """
    # Check database
    db_healthy = check_db_connection()
    
    # Check Google APIs
    api_status = validate_all_google_apis()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "services": {
            "gemini_api": "configured" if api_status.get("gemini") else "not_configured",
            "speech_to_text": "configured" if api_status.get("speech_to_text") else "not_configured",
            "google_drive": "configured" if api_status.get("google_drive") else "not_configured"
        }
    }


# Include API routers
app.include_router(notes.router, prefix=settings.API_V1_PREFIX)
app.include_router(query.router, prefix=settings.API_V1_PREFIX)
app.include_router(insights.router, prefix=settings.API_V1_PREFIX)
app.include_router(telegram_webhook.router, prefix=settings.API_V1_PREFIX)
app.include_router(gdrive.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
