"""
API routes for Google Drive integration.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.user import User
from backend.models.note import Note
from backend.services import gdrive_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gdrive", tags=["gdrive"])


@router.post("/export/{note_id}")
async def export_note_to_drive(
    note_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Export a note to Google Drive.
    
    Args:
        note_id: Note ID
        user_id: User ID
        db: Database session
        
    Returns:
        Export result with file ID and URL
    """
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.gdrive_token:
            raise HTTPException(
                status_code=400,
                detail="Google Drive not connected. Please authenticate first."
            )
        
        # Get note
        note = db.query(Note).filter(
            Note.id == note_id,
            Note.user_id == user_id
        ).first()
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Prepare note data
        note_data = {
            "title": note.title,
            "summary": note.summary,
            "primary_tag": note.primary_tag,
            "secondary_tags": note.secondary_tags,
            "key_entities": note.key_entities,
            "actionable_items": note.actionable_items,
            "topics": note.topics,
            "original_text": note.original_text,
            "transcription": note.transcription,
            "source": note.source,
            "created_at": note.created_at
        }
        
        # Export to Drive
        result = await gdrive_service.export_note_as_markdown(
            note_data=note_data,
            token_data=user.gdrive_token,
            folder_id=user.gdrive_folder_id
        )
        
        # Update note
        note.synced_to_gdrive = True
        note.gdrive_file_id = result["file_id"]
        note.gdrive_file_url = result["file_url"]
        db.commit()
        
        logger.info(f"Note exported to Google Drive: {note_id}")
        
        return {
            "status": "success",
            "file_id": result["file_id"],
            "file_url": result["file_url"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting to Google Drive: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-all")
async def export_all_notes(
    user_id: str,
    primary_tag: str = None,
    db: Session = Depends(get_db)
):
    """
    Export all notes (or filtered by tag) to Google Drive.
    
    Args:
        user_id: User ID
        primary_tag: Optional tag filter
        db: Database session
        
    Returns:
        Export summary
    """
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.gdrive_token:
            raise HTTPException(
                status_code=400,
                detail="Google Drive not connected"
            )
        
        # Get notes
        query = db.query(Note).filter(
            Note.user_id == user_id,
            Note.processing_status == "completed"
        )
        
        if primary_tag:
            query = query.filter(Note.primary_tag == primary_tag)
        
        notes = query.all()
        
        if not notes:
            return {
                "status": "success",
                "message": "No notes to export",
                "exported": 0,
                "failed": 0
            }
        
        # Export each note
        exported = 0
        failed = 0
        
        for note in notes:
            try:
                note_data = {
                    "title": note.title,
                    "summary": note.summary,
                    "primary_tag": note.primary_tag,
                    "secondary_tags": note.secondary_tags,
                    "key_entities": note.key_entities,
                    "actionable_items": note.actionable_items,
                    "topics": note.topics,
                    "original_text": note.original_text,
                    "transcription": note.transcription,
                    "source": note.source,
                    "created_at": note.created_at
                }
                
                result = await gdrive_service.export_note_as_markdown(
                    note_data=note_data,
                    token_data=user.gdrive_token,
                    folder_id=user.gdrive_folder_id
                )
                
                note.synced_to_gdrive = True
                note.gdrive_file_id = result["file_id"]
                note.gdrive_file_url = result["file_url"]
                exported += 1
                
            except Exception as e:
                logger.error(f"Error exporting note {note.id}: {e}")
                failed += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Export completed",
            "exported": exported,
            "failed": failed,
            "total": len(notes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk export: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_drive_status(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get Google Drive connection status.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Connection status
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        is_connected = user.gdrive_token is not None
        
        # Get sync stats
        total_notes = db.query(Note).filter(Note.user_id == user_id).count()
        synced_notes = db.query(Note).filter(
            Note.user_id == user_id,
            Note.synced_to_gdrive == True
        ).count()
        
        return {
            "connected": is_connected,
            "folder_id": user.gdrive_folder_id,
            "total_notes": total_notes,
            "synced_notes": synced_notes,
            "pending_sync": total_notes - synced_notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Drive status: {e}")
        raise HTTPException(status_code=500, detail=str(e))