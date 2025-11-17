"""
Configuration settings for the application.
Loads environment variables and provides centralized settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App Settings
    APP_NAME: str = "Second Brain Agent"
    ENVIRONMENT: str = "local"  # local, production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"
    
    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/secondbrain"
    USE_CLOUD_SQL: bool = False
    CLOUD_SQL_CONNECTION_NAME: Optional[str] = None
    CLOUD_SQL_DATABASE_URL: Optional[str] = None
    
    # Google Gemini API
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    # Google Speech-to-Text API
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GCP_PROJECT_ID: Optional[str] = None
    
    # Google Drive API
    GDRIVE_CLIENT_ID: Optional[str] = None
    GDRIVE_CLIENT_SECRET: Optional[str] = None
    GDRIVE_REDIRECT_URI: str = "http://localhost:8000/api/gdrive/callback"
    GDRIVE_FOLDER_ID: Optional[str] = None
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # Local Storage Paths
    LOCAL_AUDIO_DIR: str = "./data/audio"
    LOCAL_EXPORT_DIR: str = "./data/exports"
    CHROMA_PERSIST_DIR: str = "./data/vector_db"
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Audio Processing
    MAX_AUDIO_SIZE_MB: int = 25
    SUPPORTED_AUDIO_FORMATS: list = [".mp3", ".wav", ".ogg", ".m4a", ".webm"]
    
    # CORS Settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:8501",  # Streamlit
        "http://localhost:8000",  # FastAPI
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()


# Global settings instance
settings = get_settings()