"""
API routes for Telegram bot webhook.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.user import User
from backend.models.note import Note
from backend.schemas.telegram import TelegramUpdate
from backend.services import (
    telegram_service,
    transcription_service,
    classification_service,
    text_service,
    embedding_service
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle incoming Telegram webhook updates.
    
    Args:
        request: Webhook request
        db: Database session
        
    Returns:
        Success response
    """
    try:
        # Parse webhook data
        data = await request.json()
        logger.info(f"Received Telegram webhook: {data.get('update_id')}")
        
        # Parse update
        update = TelegramUpdate(**data)
        
        if not update.message:
            return {"status": "ok", "message": "No message in update"}
        
        message = update.message
        user_telegram_id = str(message.from_user.id)
        chat_id = message.chat.id
        
        # Get or create user
        user = db.query(User).filter(User.telegram_id == user_telegram_id).first()
        if not user:
            user = User(
                id=f"telegram_{user_telegram_id}",
                telegram_id=user_telegram_id,
                telegram_username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Handle voice message
        if message.voice:
            await _handle_voice_message(message, user, chat_id, db)
        
        # Handle text message
        elif message.text:
            await _handle_text_message(message, user, chat_id, db)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        # Don't raise HTTPException - Telegram doesn't need error details
        return {"status": "error", "message": str(e)}


async def _handle_voice_message(message, user: User, chat_id: int, db: Session):
    """Handle voice message from Telegram."""
    try:
        # Send processing notification
        await telegram_service.send_processing_notification(chat_id, "audio")
        
        # Download voice file
        file_id = message.voice.file_id
        audio_path = await telegram_service.download_voice_file(file_id, user.id)
        
        if not audio_path:
            await telegram_service.send_error_notification(
                chat_id,
                "Failed to download voice message"
            )
            return
        
        # Create note in database
        note = Note(
            user_id=user.id,
            input_type="audio",
            source="telegram",
            audio_url=audio_path,
            audio_duration_seconds=message.voice.duration,
            processing_status="processing"
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        
        # Transcribe audio
        transcription_result = await transcription_service.transcribe_audio(
            audio_file_path=audio_path,
            language_code="en-US"
        )
        
        note.transcription = transcription_result["text"]
        note.language = transcription_result["language"]
        
        # Classify
        classification = await classification_service.classify_note(
            text=transcription_result["text"],
            input_type="audio"
        )
        
        # Update note
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
        
        # Store embedding
        embedding_metadata = {
            "user_id": user.id,
            "primary_tag": classification.primary_tag,
            "created_at": note.created_at.isoformat()
        }
        await embedding_service.store_note_embedding(
            note_id=str(note.id),
            text=transcription_result["text"],
            metadata=embedding_metadata
        )
        
        db.commit()
        
        # Send success notification
        note_data = {
            "title": note.title,
            "primary_tag": note.primary_tag,
            "summary": note.summary,
            "actionable_items": note.actionable_items
        }
        await telegram_service.send_success_notification(chat_id, note_data)
        
        logger.info(f"Voice message processed successfully: {note.id}")
        
    except Exception as e:
        logger.error(f"Error handling voice message: {e}")
        await telegram_service.send_error_notification(
            chat_id,
            "Failed to process voice message"
        )


async def _handle_text_message(message, user: User, chat_id: int, db: Session):
    """Handle text message from Telegram."""
    try:
        text = message.text
        
        # Ignore commands
        if text.startswith("/"):
            return
        
        # Send processing notification
        await telegram_service.send_processing_notification(chat_id, "text")
        
        # Process text
        text_result = await text_service.process_text_input(
            text=text,
            user_id=user.id,
            source="telegram"
        )
        
        # Create note
        note = Note(
            user_id=user.id,
            input_type="text",
            source="telegram",
            original_text=text_result["text"],
            processing_status="processing"
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        
        # Classify
        classification = await classification_service.classify_note(
            text=text_result["text"],
            input_type="text"
        )
        
        # Update note
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
        
        # Store embedding
        embedding_metadata = {
            "user_id": user.id,
            "primary_tag": classification.primary_tag,
            "created_at": note.created_at.isoformat()
        }
        await embedding_service.store_note_embedding(
            note_id=str(note.id),
            text=text_result["text"],
            metadata=embedding_metadata
        )
        
        db.commit()
        
        # Send success notification
        note_data = {
            "title": note.title,
            "primary_tag": note.primary_tag,
            "summary": note.summary,
            "actionable_items": note.actionable_items
        }
        await telegram_service.send_success_notification(chat_id, note_data)
        
        logger.info(f"Text message processed successfully: {note.id}")
        
    except Exception as e:
        logger.error(f"Error handling text message: {e}")
        await telegram_service.send_error_notification(
            chat_id,
            "Failed to process text message"
        )


@router.get("/webhook-info")
async def get_webhook_info():
    """Get current webhook information."""
    try:
        if not telegram_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Telegram service not configured"
            )
        
        # This would require storing webhook URL in config
        return {
            "status": "configured",
            "bot_available": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail=str(e))