"""
File utility functions for handling uploads and storage.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import uuid
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Path to directory
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_user_audio_directory(user_id: str) -> str:
    """
    Get the audio directory for a specific user.
    Creates directory if it doesn't exist.
    
    Args:
        user_id: User identifier
        
    Returns:
        Path to user's audio directory
    """
    user_dir = os.path.join(settings.LOCAL_AUDIO_DIR, user_id)
    ensure_directory_exists(user_dir)
    return user_dir


def get_unique_filename(original_filename: str, user_id: str) -> str:
    """
    Generate a unique filename with timestamp and UUID.
    
    Args:
        original_filename: Original file name
        user_id: User identifier
        
    Returns:
        Unique filename
    """
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate unique name with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{user_id}_{timestamp}_{unique_id}{ext}"


def save_audio_file(file_content: bytes, filename: str, user_id: str) -> str:
    """
    Save audio file to local storage.
    
    Args:
        file_content: Binary content of the file
        filename: Name of the file
        user_id: User identifier
        
    Returns:
        Path to saved file
    """
    try:
        # Get user directory
        user_dir = get_user_audio_directory(user_id)
        
        # Generate unique filename
        unique_filename = get_unique_filename(filename, user_id)
        
        # Full path
        file_path = os.path.join(user_dir, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Audio file saved: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving audio file: {e}")
        raise


def delete_file(file_path: str) -> bool:
    """
    Delete a file from local storage.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def validate_audio_file(file_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate audio file (exists, size, format).
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    # Check file size
    file_size_mb = get_file_size(file_path) / (1024 * 1024)
    if file_size_mb > settings.MAX_AUDIO_SIZE_MB:
        return False, f"File size exceeds {settings.MAX_AUDIO_SIZE_MB}MB limit"
    
    # Check file extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in settings.SUPPORTED_AUDIO_FORMATS:
        return False, f"Unsupported audio format. Supported: {settings.SUPPORTED_AUDIO_FORMATS}"
    
    return True, None


def cleanup_temp_files(directory: str = "./data/temp") -> int:
    """
    Clean up temporary files older than 24 hours.
    
    Args:
        directory: Path to temp directory
        
    Returns:
        Number of files deleted
    """
    count = 0
    try:
        now = datetime.utcnow().timestamp()
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                # Check if file is older than 24 hours
                file_age = now - os.path.getmtime(file_path)
                if file_age > 86400:  # 24 hours in seconds
                    os.remove(file_path)
                    count += 1
        
        logger.info(f"Cleaned up {count} temporary files")
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up temp files: {e}")
        return count