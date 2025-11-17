"""
User model for storing user information and preferences.
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.core.database import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(String(255), primary_key=True)  # Can be telegram_id or generated UUID
    
    # Contact Information
    phone_number = Column(String(50), unique=True, nullable=True, index=True)
    telegram_id = Column(String(100), unique=True, nullable=True, index=True)
    telegram_username = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    
    # User Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Google Drive Integration
    gdrive_token = Column(JSON, nullable=True)  # Stores OAuth token
    gdrive_folder_id = Column(String(255), nullable=True)
    
    # User Preferences
    default_tags = Column(JSON, nullable=True)  # ["Work", "Personal"]
    auto_sync_gdrive = Column(Boolean, default=True)
    language_preference = Column(String(10), default="en")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"