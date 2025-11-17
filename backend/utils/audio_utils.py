"""
Audio processing utilities using pydub.
"""

from pydub import AudioSegment
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def convert_audio_format(input_path: str, output_format: str = "wav") -> Optional[str]:
    """
    Convert audio file to specified format.
    
    Args:
        input_path: Path to input audio file
        output_format: Desired output format (wav, mp3, etc.)
        
    Returns:
        Path to converted file or None if conversion failed
    """
    try:
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Generate output path
        base_path = os.path.splitext(input_path)[0]
        output_path = f"{base_path}_converted.{output_format}"
        
        # Export in new format
        audio.export(output_path, format=output_format)
        
        logger.info(f"Audio converted: {input_path} -> {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error converting audio: {e}")
        return None


def get_audio_duration(file_path: str) -> Optional[int]:
    """
    Get audio duration in seconds.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds or None if failed
    """
    try:
        audio = AudioSegment.from_file(file_path)
        duration_seconds = len(audio) / 1000  # pydub uses milliseconds
        return int(duration_seconds)
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return None


def normalize_audio(input_path: str) -> Optional[str]:
    """
    Normalize audio volume.
    
    Args:
        input_path: Path to input audio file
        
    Returns:
        Path to normalized file or None if failed
    """
    try:
        audio = AudioSegment.from_file(input_path)
        
        # Normalize to -20 dBFS
        normalized_audio = audio.apply_gain(-20 - audio.dBFS)
        
        # Save normalized version
        base_path = os.path.splitext(input_path)[0]
        output_path = f"{base_path}_normalized.wav"
        
        normalized_audio.export(output_path, format="wav")
        
        logger.info(f"Audio normalized: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error normalizing audio: {e}")
        return None