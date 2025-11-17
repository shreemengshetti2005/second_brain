"""
Main runner script for Second Brain Agent.
Starts both FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import streamlit
        import sqlalchemy
        import chromadb
        logger.info("✅ All dependencies installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Run: pip install -r requirements.txt")
        return False


def check_database():
    """Check if database is accessible."""
    try:
        from backend.core.database import check_db_connection
        if check_db_connection():
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.warning("⚠️  Database connection failed")
            logger.warning("Make sure PostgreSQL is running and database is created")
            return False
    except Exception as e:
        logger.error(f"❌ Database check failed: {e}")
        return False


def start_backend():
    """Start FastAPI backend server."""
    logger.info("🚀 Starting FastAPI backend on http://localhost:8000")
    
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return backend_process


def start_frontend():
    """Start Streamlit frontend."""
    logger.info("🚀 Starting Streamlit frontend on http://localhost:8501")
    
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return frontend_process


def main():
    """Main entry point."""
    
    print("="*60)
    print("🧠 SECOND BRAIN AGENT - STARTING...")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database
    if not check_database():
        logger.warning("⚠️  Continuing without database connection")
        logger.warning("Some features may not work correctly")
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(3)  # Wait for backend to start
        
        # Start frontend
        frontend_process = start_frontend()
        time.sleep(2)  # Wait for frontend to start
        
        print("\n" + "="*60)
        print("✅ APPLICATION STARTED SUCCESSFULLY!")
        print("="*60)
        print("\n📍 ENDPOINTS:")
        print("   🌐 Web Interface:  http://localhost:8501")
        print("   🔧 API Backend:    http://localhost:8000")
        print("   📚 API Docs:       http://localhost:8000/docs")
        print("\n⌨️  Press Ctrl+C to stop all services")
        print("="*60 + "\n")
        
        # Wait for processes
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down...")
            backend_process.terminate()
            frontend_process.terminate()
            backend_process.wait()
            frontend_process.wait()
            logger.info("✅ All services stopped")
            
    except Exception as e:
        logger.error(f"❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()