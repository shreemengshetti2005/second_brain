"""
API routes for searching and querying notes.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.schemas.query import SearchRequest
from backend.schemas.note import NoteListResponse, NoteResponse
from backend.services import search_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["query"])


@router.post("/search", response_model=NoteListResponse)
async def search_notes(
    search_request: SearchRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Search notes with filters and optional semantic search.
    
    Args:
        search_request: Search parameters
        user_id: User ID
        db: Database session
        
    Returns:
        Search results
    """
    try:
        logger.info(f"Searching notes for user {user_id}")
        
        # Perform search
        notes, total = await search_service.search_notes(
            db=db,
            search_request=search_request,
            user_id=user_id
        )
        
        # Calculate total pages
        total_pages = (total + search_request.page_size - 1) // search_request.page_size
        
        return NoteListResponse(
            notes=notes,
            total=total,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error searching notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=List[NoteResponse])
async def get_recent_notes(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent notes for a user.
    
    Args:
        user_id: User ID
        limit: Number of notes to return
        db: Database session
        
    Returns:
        List of recent notes
    """
    try:
        notes = await search_service.get_recent_notes(
            db=db,
            user_id=user_id,
            limit=limit
        )
        
        return notes
        
    except Exception as e:
        logger.error(f"Error getting recent notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))