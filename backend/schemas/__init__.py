"""Pydantic schemas for API requests and responses."""

from backend.schemas.note import (
    NoteCreate,
    NoteAudioCreate,
    NoteClassification,
    NoteUpdate,
    NoteResponse,
    NoteListResponse,
)
from backend.schemas.query import (
    SearchRequest,
    InsightRequest,
    InsightResponse,
)
from backend.schemas.telegram import (
    TelegramUpdate,
    TelegramMessage,
    TelegramVoice,
)
from backend.schemas.insight import (
    AnalyticsResponse,
    TagDistribution,
    ActivityPattern,
    TopEntity,
)

__all__ = [
    "NoteCreate",
    "NoteAudioCreate",
    "NoteClassification",
    "NoteUpdate",
    "NoteResponse",
    "NoteListResponse",
    "SearchRequest",
    "InsightRequest",
    "InsightResponse",
    "TelegramUpdate",
    "TelegramMessage",
    "TelegramVoice",
    "AnalyticsResponse",
    "TagDistribution",
    "ActivityPattern",
    "TopEntity",
]