"""
API routes for generating insights and analytics.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from backend.core.database import get_db
from backend.models.note import Note
from backend.schemas.query import InsightRequest, InsightResponse
from backend.schemas.insight import (
    AnalyticsResponse,
    TagDistribution,
    ActivityPattern,
    TopEntity
)
from backend.services import insight_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/insights", tags=["insights"])


@router.post("/generate", response_model=InsightResponse)
async def generate_insights(
    insight_request: InsightRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered insights from notes.
    
    Args:
        insight_request: Insight generation parameters
        user_id: User ID
        db: Database session
        
    Returns:
        Generated insights
    """
    try:
        logger.info(f"Generating insights for user {user_id}: {insight_request.query}")
        
        insights = await insight_service.generate_insights(
            db=db,
            user_id=user_id,
            insight_request=insight_request
        )
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get analytics and statistics for user's notes.
    
    Args:
        user_id: User ID
        days: Number of days to analyze
        db: Database session
        
    Returns:
        Analytics data
    """
    try:
        logger.info(f"Getting analytics for user {user_id} (last {days} days)")
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get all notes in range
        notes = db.query(Note).filter(
            Note.user_id == user_id,
            Note.created_at >= start_date,
            Note.processing_status == "completed"
        ).all()
        
        # Total notes
        total_notes = len(notes)
        
        # Notes by type
        notes_by_type = {}
        for note in notes:
            input_type = note.input_type or "unknown"
            notes_by_type[input_type] = notes_by_type.get(input_type, 0) + 1
        
        # Notes by source
        notes_by_source = {}
        for note in notes:
            source = note.source or "unknown"
            notes_by_source[source] = notes_by_source.get(source, 0) + 1
        
        # Tag distribution
        tag_counts = {}
        for note in notes:
            tag = note.primary_tag or "Other"
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        tag_distribution = [
            TagDistribution(
                tag=tag,
                count=count,
                percentage=round((count / total_notes * 100), 2) if total_notes > 0 else 0
            )
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Activity by hour
        activity_by_hour = [0] * 24
        for note in notes:
            hour = note.created_at.hour
            activity_by_hour[hour] += 1
        
        activity_patterns = [
            ActivityPattern(hour=i, count=count)
            for i, count in enumerate(activity_by_hour)
            if count > 0
        ]
        
        # Top entities
        entity_counts = {}
        for note in notes:
            if note.key_entities:
                for entity_type, entities in note.key_entities.items():
                    for entity in entities:
                        key = (entity, entity_type)
                        entity_counts[key] = entity_counts.get(key, 0) + 1
        
        top_entities = [
            TopEntity(name=entity, count=count, type=entity_type)
            for (entity, entity_type), count in sorted(
                entity_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        ]
        
        # Pending action items
        pending_action_items = 0
        for note in notes:
            if note.actionable_items:
                pending_action_items += len(note.actionable_items)
        
        return AnalyticsResponse(
            total_notes=total_notes,
            notes_by_type=notes_by_type,
            notes_by_source=notes_by_source,
            tag_distribution=tag_distribution,
            activity_by_hour=activity_patterns,
            top_entities=top_entities,
            pending_action_items=pending_action_items,
            date_range={
                "start": start_date,
                "end": end_date
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/action-items")
async def get_action_items(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get all action items from notes.
    
    Args:
        user_id: User ID
        limit: Maximum number of action items
        db: Database session
        
    Returns:
        List of action items
    """
    try:
        notes = db.query(Note).filter(
            Note.user_id == user_id,
            Note.actionable_items.isnot(None),
            Note.processing_status == "completed"
        ).order_by(Note.created_at.desc()).limit(limit).all()
        
        action_items = []
        for note in notes:
            if note.actionable_items:
                for item in note.actionable_items:
                    action_items.append({
                        "note_id": str(note.id),
                        "note_title": note.title,
                        "task": item.get("task", ""),
                        "deadline": item.get("deadline"),
                        "priority": item.get("priority", "medium"),
                        "created_at": note.created_at.isoformat()
                    })
        
        return {"action_items": action_items, "total": len(action_items)}
        
    except Exception as e:
        logger.error(f"Error getting action items: {e}")
        raise HTTPException(status_code=500, detail=str(e))