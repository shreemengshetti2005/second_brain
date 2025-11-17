"""
Audio service for handling audio file processing.
Validates, converts, and prepares audio for transcription.
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple

from backend.core.config import settings
from backend.utils.audio_utils import (
    convert_audio_format,
    get_audio_duration,
    normalize_audio
)
from backend.utils.file_utils import (
    save_audio_file,
    validate_audio_file,
    get_file_size
)

logger = logging.getLogger(__name__)


class AudioService:
    """Service for audio file processing."""
    
    async def process_audio_upload(
        self,
        file_content: bytes,
        filename: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Process uploaded audio file.
        
        Args:
            file_content: Binary content of audio file
            filename: Original filename
            user_id: User ID
            
        Returns:
            Dictionary with audio processing results:
            {
                "audio_path": str,
                "duration_seconds": int,
                "file_size_bytes": int,
                "format": str
            }
        """
        try:
            logger.info(f"Processing audio upload for user {user_id}: {filename}")
            
            # Save audio file
            audio_path = save_audio_file(file_content, filename, user_id)
            
            # Validate audio file
            is_valid, error_msg = validate_audio_file(audio_path)
            if not is_valid:
                logger.error(f"Audio validation failed: {error_msg}")
                raise ValueError(error_msg)
            
            # Get file info
            file_size = get_file_size(audio_path)
            duration = get_audio_duration(audio_path)
            
            # Get format
            _, ext = os.path.splitext(audio_path)
            audio_format = ext.lower().replace('.', '')
            
            logger.info(
                f"Audio processed successfully: {audio_path}, "
                f"duration: {duration}s, size: {file_size} bytes"
            )
            
            return {
                "audio_path": audio_path,
                "duration_seconds": duration or 0,
                "file_size_bytes": file_size,
                "format": audio_format
            }
            
        except Exception as e:
            logger.error(f"Error processing audio upload: {e}")
            raise
    
    async def prepare_audio_for_transcription(
        self,
        audio_path: str
    ) -> str:
        """
        Prepare audio file for transcription (convert to optimal format).
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Path to prepared audio file
        """
        try:
            # Check if conversion is needed
            _, ext = os.path.splitext(audio_path)
            
            # If already in WAV format, return as is
            if ext.lower() == '.wav':
                logger.info("Audio already in WAV format")
                return audio_path
            
            # Convert to WAV for better compatibility
            logger.info(f"Converting audio to WAV format: {audio_path}")
            converted_path = convert_audio_format(audio_path, "wav")
            
            if converted_path:
                logger.info(f"Audio converted successfully: {converted_path}")
                return converted_path
            else:
                logger.warning("Audio conversion failed, using original file")
                return audio_path
            
        except Exception as e:
            logger.error(f"Error preparing audio for transcription: {e}")
            # Return original path if preparation fails
            return audio_path
    
    async def validate_audio_for_upload(
        self,
        file_size_bytes: int,
        filename: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate audio file before upload.
        
        Args:
            file_size_bytes: Size of file in bytes
            filename: Filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        max_size_bytes = settings.MAX_AUDIO_SIZE_MB * 1024 * 1024
        if file_size_bytes > max_size_bytes:
            return False, f"File size exceeds {settings.MAX_AUDIO_SIZE_MB}MB limit"
        
        # Check file extension
        _, ext = os.path.splitext(filename)
        if ext.lower() not in settings.SUPPORTED_AUDIO_FORMATS:
            return False, f"Unsupported format. Supported: {settings.SUPPORTED_AUDIO_FORMATS}"
        
        return True, None


# Global instance
audio_service = AudioService()