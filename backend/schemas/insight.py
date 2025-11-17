"""
Pydantic schemas for insights and analytics.
"""

from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime


class TagDistribution(BaseModel):
    """Tag distribution statistics."""
    tag: str
    count: int
    percentage: float


class ActivityPattern(BaseModel):
    """Activity pattern statistics."""
    hour: int
    count: int


class TopEntity(BaseModel):
    """Top mentioned entity."""
    name: str
    count: int
    type: str  # person, place, company, etc.


class AnalyticsResponse(BaseModel):
    """Schema for analytics response."""
    total_notes: int
    notes_by_type: Dict[str, int]
    notes_by_source: Dict[str, int]
    tag_distribution: List[TagDistribution]
    activity_by_hour: List[ActivityPattern]
    top_entities: List[TopEntity]
    pending_action_items: int
    date_range: Dict[str, datetime]