"""
Note model for storing voice and text notes with AI-generated metadata.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.core.database import Base


class Note(Base):
    """Note model for storing audio and text notes."""
    
    __tablename__ = "notes"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    user_id = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Input Information
    input_type = Column(String(20), nullable=False)  # "audio" or "text"
    source = Column(String(50), nullable=False)  # "telegram", "web", "api"
    
    # Content
    original_text = Column(Text, nullable=True)  # For text input
    transcription = Column(Text, nullable=True)  # For audio transcription
    audio_url = Column(String(500), nullable=True)  # Local path or URL
    audio_duration_seconds = Column(Integer, nullable=True)
    
    # AI-Generated Metadata
    title = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    primary_tag = Column(String(50), nullable=True, index=True)
    secondary_tags = Column(ARRAY(String), nullable=True)
    
    # Extracted Entities
    key_entities = Column(JSON, nullable=True)  # {people: [], places: [], dates: [], companies: []}
    actionable_items = Column(JSON, nullable=True)  # [{task, deadline, priority}]
    topics = Column(ARRAY(String), nullable=True)
    
    # Sentiment & Priority
    sentiment = Column(String(20), nullable=True)  # positive, neutral, negative
    priority = Column(String(20), nullable=True)  # high, medium, low
    
    # Language
    language = Column(String(10), default="en")
    
    # Embeddings
    embedding_id = Column(String(255), nullable=True)  # Reference to vector DB
    
    # Sync Status
    synced_to_gdrive = Column(Boolean, default=False)
    gdrive_file_id = Column(String(255), nullable=True)
    gdrive_file_url = Column(String(500), nullable=True)
    
    # Processing Status
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    
    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title}, type={self.input_type})>"
    
    def get_text_content(self) -> str:
        """Get the text content (either original text or transcription)."""
        if self.input_type == "text":
            return self.original_text or ""
        else:
            return self.transcription or ""