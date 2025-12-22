"""
API routes for user management.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_current_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current user information.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User information
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "telegram_username": user.telegram_username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "gdrive_connected": user.gdrive_token is not None,
            "gdrive_folder_id": user.gdrive_folder_id,
            "language_preference": user.language_preference,
            "created_at": user.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences")
async def update_preferences(
    user_id: str,
    preferences: dict,
    db: Session = Depends(get_db)
):
    """
    Update user preferences.
    
    Args:
        user_id: User ID
        preferences: Preferences to update
        db: Database session
        
    Returns:
        Updated user
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update allowed preferences
        if "language_preference" in preferences:
            user.language_preference = preferences["language_preference"]
        
        if "auto_sync_gdrive" in preferences:
            user.auto_sync_gdrive = preferences["auto_sync_gdrive"]
        
        if "default_tags" in preferences:
            user.default_tags = preferences["default_tags"]
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User preferences updated: {user_id}")
        return {"status": "success", "message": "Preferences updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
