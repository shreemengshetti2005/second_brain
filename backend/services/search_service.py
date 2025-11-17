"""
Search service for finding notes using text search and semantic search.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime

from backend.models.note import Note
from backend.services.embedding_service import embedding_service
from backend.schemas.query import SearchRequest

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching notes."""
    
    async def search_notes(
        self,
        db: Session,
        search_request: SearchRequest,
        user_id: str
    ) -> tuple[List[Note], int]:
        """
        Search notes based on criteria.
        
        Args:
            db: Database session
            search_request: Search request parameters
            user_id: User ID
            
        Returns:
            Tuple of (notes, total_count)
        """
        try:
            logger.info(f"Searching notes for user {user_id}")
            
            # Build base query
            query = db.query(Note).filter(Note.user_id == user_id)
            
            # Apply filters
            query = self._apply_filters(query, search_request)
            
            # Get total count
            total_count = query.count()
            
            # Apply text search if query provided
            if search_request.query and not search_request.use_semantic_search:
                query = self._apply_text_search(query, search_request.query)
            
            # Apply sorting
            query = query.order_by(Note.created_at.desc())
            
            # Apply pagination
            offset = (search_request.page - 1) * search_request.page_size
            query = query.offset(offset).limit(search_request.page_size)
            
            # Execute query
            notes = query.all()
            
            # If semantic search requested, re-rank results
            if search_request.query and search_request.use_semantic_search:
                notes = await self._semantic_search(
                    db,
                    user_id,
                    search_request.query,
                    search_request
                )
            
            logger.info(f"Found {len(notes)} notes (total: {total_count})")
            return notes, total_count
            
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            raise
    
    def _apply_filters(
        self,
        query,
        search_request: SearchRequest
    ):
        """Apply filters to query."""
        
        # Filter by primary tag
        if search_request.primary_tag:
            query = query.filter(Note.primary_tag == search_request.primary_tag)
        
        # Filter by source
        if search_request.source:
            query = query.filter(Note.source == search_request.source)
        
        # Filter by date range
        if search_request.start_date:
            query = query.filter(Note.created_at >= search_request.start_date)
        
        if search_request.end_date:
            query = query.filter(Note.created_at <= search_request.end_date)
        
        # Only show completed notes
        query = query.filter(Note.processing_status == "completed")
        
        return query
    
    def _apply_text_search(self, query, search_text: str):
        """Apply text search to query."""
        
        search_pattern = f"%{search_text}%"
        
        query = query.filter(
            or_(
                Note.title.ilike(search_pattern),
                Note.summary.ilike(search_pattern),
                Note.original_text.ilike(search_pattern),
                Note.transcription.ilike(search_pattern)
            )
        )
        
        return query
    
    async def _semantic_search(
        self,
        db: Session,
        user_id: str,
        query_text: str,
        search_request: SearchRequest
    ) -> List[Note]:
        """
        Perform semantic search using embeddings.
        
        Args:
            db: Database session
            user_id: User ID
            query_text: Search query
            search_request: Search parameters
            
        Returns:
            List of notes sorted by relevance
        """
        try:
            # Build metadata filter
            filter_metadata = {"user_id": user_id}
            
            if search_request.primary_tag:
                filter_metadata["primary_tag"] = search_request.primary_tag
            
            # Search using embedding service
            similar_notes = await embedding_service.search_similar_notes(
                query_text=query_text,
                n_results=search_request.page_size * 2,  # Get more for filtering
                filter_metadata=filter_metadata
            )
            
            # Get note IDs
            note_ids = [n["note_id"] for n in similar_notes]
            
            if not note_ids:
                return []
            
            # Fetch notes from database
            notes = db.query(Note).filter(Note.id.in_(note_ids)).all()
            
            # Sort by similarity (preserve order from vector search)
            note_dict = {str(note.id): note for note in notes}
            sorted_notes = [note_dict[nid] for nid in note_ids if nid in note_dict]
            
            # Apply pagination
            offset = (search_request.page - 1) * search_request.page_size
            return sorted_notes[offset:offset + search_request.page_size]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            # Fallback to empty list
            return []
    
    async def get_note_by_id(
        self,
        db: Session,
        note_id: str,
        user_id: str
    ) -> Optional[Note]:
        """
        Get note by ID.
        
        Args:
            db: Database session
            note_id: Note ID
            user_id: User ID
            
        Returns:
            Note or None
        """
        return db.query(Note).filter(
            and_(Note.id == note_id, Note.user_id == user_id)
        ).first()
    
    async def get_recent_notes(
        self,
        db: Session,
        user_id: str,
        limit: int = 10
    ) -> List[Note]:
        """
        Get recent notes for user.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Number of notes to return
            
        Returns:
            List of recent notes
        """
        return db.query(Note).filter(
            and_(
                Note.user_id == user_id,
                Note.processing_status == "completed"
            )
        ).order_by(Note.created_at.desc()).limit(limit).all()


# Global instance
search_service = SearchService()