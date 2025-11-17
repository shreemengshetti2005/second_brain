"""
Pydantic schemas for Note API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class NoteBase(BaseModel):
    """Base note schema with common fields."""
    input_type: str = Field(..., description="Type of input: 'audio' or 'text'")
    source: str = Field(..., description="Source: 'telegram', 'web', 'api'")
    

class NoteCreate(NoteBase):
    """Schema for creating a new note (text input)."""
    original_text: str = Field(..., description="Text content of the note")
    user_id: str = Field(..., description="User ID")
    
    @validator('input_type')
    def validate_input_type(cls, v):
        if v not in ['audio', 'text']:
            raise ValueError("input_type must be 'audio' or 'text'")
        return v
    
    @validator('source')
    def validate_source(cls, v):
        if v not in ['telegram', 'web', 'api']:
            raise ValueError("source must be 'telegram', 'web', or 'api'")
        return v


class NoteAudioCreate(NoteBase):
    """Schema for creating a note from audio (internal use after transcription)."""
    transcription: str
    audio_url: str
    audio_duration_seconds: Optional[int] = None
    user_id: str
    language: str = "en"


class NoteClassification(BaseModel):
    """Schema for AI classification results."""
    title: str
    summary: str
    primary_tag: str
    secondary_tags: List[str] = []
    key_entities: Dict[str, List[str]] = Field(
        default_factory=lambda: {"people": [], "places": [], "dates": [], "companies": []}
    )
    actionable_items: List[Dict[str, Any]] = []
    topics: List[str] = []
    sentiment: str = "neutral"
    priority: str = "medium"


class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = None
    summary: Optional[str] = None
    primary_tag: Optional[str] = None
    secondary_tags: Optional[List[str]] = None
    
    class Config:
        extra = "forbid"


class NoteResponse(BaseModel):
    """Schema for note response."""
    id: UUID
    user_id: str
    input_type: str
    source: str
    original_text: Optional[str] = None
    transcription: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration_seconds: Optional[int] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    primary_tag: Optional[str] = None
    secondary_tags: Optional[List[str]] = None
    key_entities: Optional[Dict[str, List[str]]] = None
    actionable_items: Optional[List[Dict[str, Any]]] = None
    topics: Optional[List[str]] = None
    sentiment: Optional[str] = None
    priority: Optional[str] = None
    language: str
    synced_to_gdrive: bool
    gdrive_file_id: Optional[str] = None
    gdrive_file_url: Optional[str] = None
    processing_status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allows compatibility with SQLAlchemy models


class NoteListResponse(BaseModel):
    """Schema for paginated list of notes."""
    notes: List[NoteResponse]
    total: int
    page: int
    page_size: int
    total_pages: int