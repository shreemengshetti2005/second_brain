"""
Pydantic schemas for search and query operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SearchRequest(BaseModel):
    """Schema for search request."""
    query: Optional[str] = Field(None, description="Search query text")
    primary_tag: Optional[str] = Field(None, description="Filter by primary tag")
    source: Optional[str] = Field(None, description="Filter by source")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    use_semantic_search: bool = Field(False, description="Use vector similarity search")


class InsightRequest(BaseModel):
    """Schema for generating insights."""
    query: str = Field(..., description="Natural language query for insights")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    primary_tag: Optional[str] = Field(None, description="Filter by tag")
    max_notes: int = Field(50, ge=1, le=200, description="Maximum notes to analyze")


class InsightResponse(BaseModel):
    """Schema for insight response."""
    query: str
    insight: str
    notes_analyzed: int
    related_notes: List[str] = []  # List of note IDs
    summary_points: List[str] = []
    action_items: List[str] = []