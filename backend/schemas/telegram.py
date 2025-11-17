"""
Pydantic schemas for Telegram webhook payloads.
"""

from pydantic import BaseModel, Field
from typing import Optional


class TelegramUser(BaseModel):
    """Telegram user information."""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    """Telegram chat information."""
    id: int
    type: str
    first_name: Optional[str] = None
    username: Optional[str] = None


class TelegramVoice(BaseModel):
    """Telegram voice message information."""
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class TelegramMessage(BaseModel):
    """Telegram message."""
    message_id: int
    from_user: TelegramUser = Field(..., alias="from")
    chat: TelegramChat
    date: int
    text: Optional[str] = None
    voice: Optional[TelegramVoice] = None
    
    class Config:
        populate_by_name = True


class TelegramUpdate(BaseModel):
    """Telegram webhook update."""
    update_id: int
    message: Optional[TelegramMessage] = None