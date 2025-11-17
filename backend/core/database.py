"""
Database connection and session management.
Supports both local PostgreSQL and Cloud SQL.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_database_url() -> str:
    """
    Get database URL based on environment settings.
    Returns Cloud SQL URL if USE_CLOUD_SQL is True, otherwise local URL.
    """
    if settings.USE_CLOUD_SQL and settings.CLOUD_SQL_DATABASE_URL:
        logger.info("Using Cloud SQL database")
        return settings.CLOUD_SQL_DATABASE_URL
    else:
        logger.info("Using local PostgreSQL database")
        return settings.DATABASE_URL


# Create database engine
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    Usage in FastAPI routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Call this once when setting up the application.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    Returns True if connection is successful, False otherwise.
    """
    try:
        db = SessionLocal()
        # Use text() wrapper for SQLAlchemy 2.0
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False