"""
API routes for note operations (CRUD).
Handles both audio and text note creation.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID

from backend.core.database import get_db
from backend.models.note import Note
from backend.models.user import User
from backend.schemas.note import (
    NoteCreate,
    NoteResponse,
    NoteListResponse,
    NoteUpdate
)
from backend.services import (
    audio_service,
    text_service,
    transcription_service,
    classification_service,
    embedding_service
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/text", response_model=NoteResponse, status_code=201)
async def create_text_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new text note.
    
    Args:
        note_data: Note creation data
        db: Database session
        
    Returns:
        Created note
    """
    try:
        logger.info(f"Creating text note for user: {note_data.user_id}")
        
        # Get or create user
        user = db.query(User).filter(User.id == note_data.user_id).first()
        if not user:
            user = User(id=note_data.user_id)
            db.add(user)
            db.commit()
        
        # Process text
        text_result = await text_service.process_text_input(
            text=note_data.original_text,
            user_id=note_data.user_id,
            source=note_data.source
        )
        
        # Create note in database with pending status
        note = Note(
            user_id=note_data.user_id,
            input_type="text",
            source=note_data.source,
            original_text=text_result["text"],
            processing_status="processing"
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        
        # Classify note using AI
        try:
            classification = await classification_service.classify_note(
                text=text_result["text"],
                input_type="text"
            )
            
            # Update note with classification
            note.title = classification.title
            note.summary = classification.summary
            note.primary_tag = classification.primary_tag
            note.secondary_tags = classification.secondary_tags
            note.key_entities = classification.key_entities
            note.actionable_items = classification.actionable_items
            note.topics = classification.topics
            note.sentiment = classification.sentiment
            note.priority = classification.priority
            note.processing_status = "completed"
            
            # Generate and store embedding
            embedding_metadata = {
                "user_id": note_data.user_id,
                "primary_tag": classification.primary_tag,
                "created_at": note.created_at.isoformat()
            }
            
            await embedding_service.store_note_embedding(
                note_id=str(note.id),
                text=text_result["text"],
                metadata=embedding_metadata
            )
            
        except Exception as e:
            logger.error(f"Error classifying note: {e}")
            note.processing_status = "failed"
            note.error_message = str(e)
        
        db.commit()
        db.refresh(note)
        
        logger.info(f"Text note created: {note.id}")
        return note
        
    except Exception as e:
        logger.error(f"Error creating text note: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audio", response_model=NoteResponse, status_code=201)
async def create_audio_note(
    audio_file: UploadFile = File(...),
    user_id: str = Form(...),
    source: str = Form(default="web"),
    db: Session = Depends(get_db)
):
    """
    Create a new audio note.
    
    Args:
        audio_file: Audio file upload
        user_id: User ID
        source: Source of the note
        db: Database session
        
    Returns:
        Created note
    """
    try:
        logger.info(f"Creating audio note for user: {user_id}")
        
        # Get or create user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id)
            db.add(user)
            db.commit()
        
        # Read audio file
        audio_content = await audio_file.read()
        
        # Validate audio
        is_valid, error_msg = await audio_service.validate_audio_for_upload(
            file_size_bytes=len(audio_content),
            filename=audio_file.filename
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Process audio
        audio_result = await audio_service.process_audio_upload(
            file_content=audio_content,
            filename=audio_file.filename,
            user_id=user_id
        )
        
        # Create note in database with pending status
        note = Note(
            user_id=user_id,
            input_type="audio",
            source=source,
            audio_url=audio_result["audio_path"],
            audio_duration_seconds=audio_result["duration_seconds"],
            processing_status="processing"
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        
        # Transcribe audio
        try:
            # Prepare audio for transcription
            prepared_audio = await audio_service.prepare_audio_for_transcription(
                audio_result["audio_path"]
            )
            
            # Transcribe
            transcription_result = await transcription_service.transcribe_audio(
                audio_file_path=prepared_audio,
                language_code="en-US"
            )
            
            note.transcription = transcription_result["text"]
            note.language = transcription_result["language"]
            
            # Classify transcription
            classification = await classification_service.classify_note(
                text=transcription_result["text"],
                input_type="audio"
            )
            
            # Update note with classification
            note.title = classification.title
            note.summary = classification.summary
            note.primary_tag = classification.primary_tag
            note.secondary_tags = classification.secondary_tags
            note.key_entities = classification.key_entities
            note.actionable_items = classification.actionable_items
            note.topics = classification.topics
            note.sentiment = classification.sentiment
            note.priority = classification.priority
            note.processing_status = "completed"
            
            # Generate and store embedding
            embedding_metadata = {
                "user_id": user_id,
                "primary_tag": classification.primary_tag,
                "created_at": note.created_at.isoformat()
            }
            
            await embedding_service.store_note_embedding(
                note_id=str(note.id),
                text=transcription_result["text"],
                metadata=embedding_metadata
            )
            
        except Exception as e:
            logger.error(f"Error processing audio note: {e}")
            note.processing_status = "failed"
            note.error_message = str(e)
        
        db.commit()
        db.refresh(note)
        
        logger.info(f"Audio note created: {note.id}")
        return note
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating audio note: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=NoteListResponse)
async def list_notes(
    user_id: str,
    page: int = 1,
    page_size: int = 10,
    primary_tag: str = None,
    db: Session = Depends(get_db)
):
    """
    List notes for a user with pagination.
    
    Args:
        user_id: User ID
        page: Page number
        page_size: Items per page
        primary_tag: Filter by tag
        db: Database session
        
    Returns:
        Paginated list of notes
    """
    try:
        # Build query
        query = db.query(Note).filter(Note.user_id == user_id)
        
        if primary_tag:
            query = query.filter(Note.primary_tag == primary_tag)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        notes = query.order_by(Note.created_at.desc()).offset(offset).limit(page_size).all()
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return NoteListResponse(
            notes=notes,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error listing notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: UUID,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific note by ID.
    
    Args:
        note_id: Note ID
        user_id: User ID
        db: Database session
        
    Returns:
        Note details
    """
    try:
        note = db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user_id
        ).first()
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return note
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting note: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    user_id: str,
    note_update: NoteUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a note.
    
    Args:
        note_id: Note ID
        user_id: User ID
        note_update: Update data
        db: Database session
        
    Returns:
        Updated note
    """
    try:
        note = db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user_id
        ).first()
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Update fields
        if note_update.title is not None:
            note.title = note_update.title
        
        if note_update.summary is not None:
            note.summary = note_update.summary
        
        if note_update.primary_tag is not None:
            note.primary_tag = note_update.primary_tag
        
        if note_update.secondary_tags is not None:
            note.secondary_tags = note_update.secondary_tags
        
        db.commit()
        db.refresh(note)
        
        logger.info(f"Note updated: {note_id}")
        return note
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating note: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: UUID,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a note.
    
    Args:
        note_id: Note ID
        user_id: User ID
        db: Database session
    """
    try:
        note = db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user_id
        ).first()
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Delete embedding
        await embedding_service.delete_note_embedding(str(note_id))
        
        # Delete note
        db.delete(note)
        db.commit()
        
        logger.info(f"Note deleted: {note_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))