"""
Transcription service using Google Speech-to-Text API.
Converts audio files to text with language detection.
"""

import os
import logging
from typing import Dict, Optional
from google.cloud import speech_v1
from google.cloud.speech_v1 import types

from backend.core.config import settings
from backend.utils.google_api_utils import (
    validate_speech_to_text_credentials,
    log_api_usage
)

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio to text using Google Speech-to-Text."""
    
    def __init__(self):
        """Initialize the transcription service."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Google Speech-to-Text client."""
        try:
            if not validate_speech_to_text_credentials():
                logger.warning(
                    "Speech-to-Text credentials not configured. "
                    "Transcription service will not be available."
                )
                return
            
            # Set credentials environment variable
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
            
            # Initialize client
            self.client = speech_v1.SpeechClient()
            logger.info("Speech-to-Text client initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Speech-to-Text client: {e}")
            self.client = None
    
    async def transcribe_audio(
        self, 
        audio_file_path: str,
        language_code: str = "en-US",
        enable_automatic_punctuation: bool = True
    ) -> Dict[str, any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to audio file
            language_code: Language code (e.g., 'en-US', 'es-ES')
            enable_automatic_punctuation: Whether to add punctuation
            
        Returns:
            Dictionary with transcription results:
            {
                "text": str,
                "confidence": float,
                "language": str,
                "duration": float (seconds)
            }
        """
        if not self.client:
            error_msg = "Speech-to-Text client not initialized"
            logger.error(error_msg)
            log_api_usage("speech_to_text", "transcribe", False, error_msg)
            raise Exception(error_msg)
        
        try:
            logger.info(f"Starting transcription for: {audio_file_path}")
            
            # Read audio file
            with open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()
            
            # Configure audio
            audio = speech_v1.RecognitionAudio(content=content)
            
            # Configure recognition
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code=language_code,
                enable_automatic_punctuation=enable_automatic_punctuation,
                model="latest_long",  # Best for longer audio
                use_enhanced=True,  # Enhanced model for better accuracy
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            # Process results
            if not response.results:
                logger.warning("No transcription results returned")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": language_code,
                    "duration": 0.0
                }
            
            # Combine all transcription results
            transcript = ""
            total_confidence = 0.0
            num_alternatives = 0
            
            for result in response.results:
                alternative = result.alternatives[0]
                transcript += alternative.transcript + " "
                total_confidence += alternative.confidence
                num_alternatives += 1
            
            # Calculate average confidence
            avg_confidence = total_confidence / num_alternatives if num_alternatives > 0 else 0.0
            
            # Clean up transcript
            transcript = transcript.strip()
            
            logger.info(f"Transcription completed: {len(transcript)} characters, confidence: {avg_confidence:.2f}")
            log_api_usage("speech_to_text", "transcribe", True, f"{len(transcript)} chars")
            
            return {
                "text": transcript,
                "confidence": avg_confidence,
                "language": language_code,
                "duration": 0.0  # Duration calculation would require audio analysis
            }
            
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            logger.error(error_msg)
            log_api_usage("speech_to_text", "transcribe", False, error_msg)
            raise
    
    async def transcribe_audio_with_language_detection(
        self,
        audio_file_path: str
    ) -> Dict[str, any]:
        """
        Transcribe audio with automatic language detection.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dictionary with transcription results
        """
        if not self.client:
            raise Exception("Speech-to-Text client not initialized")
        
        try:
            logger.info(f"Starting transcription with language detection: {audio_file_path}")
            
            # Read audio file
            with open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()
            
            audio = speech_v1.RecognitionAudio(content=content)
            
            # Configure with multiple language hints
            config = speech_v1.RecognitionConfig(
                encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code="en-US",  # Primary language
                alternative_language_codes=["es-ES", "fr-FR", "de-DE", "hi-IN"],  # Alternative languages
                enable_automatic_punctuation=True,
                model="latest_long",
            )
            
            # Perform transcription
            response = self.client.recognize(config=config, audio=audio)
            
            if not response.results:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": "en-US",
                    "duration": 0.0
                }
            
            # Get best result
            result = response.results[0]
            alternative = result.alternatives[0]
            detected_language = result.language_code if hasattr(result, 'language_code') else "en-US"
            
            logger.info(f"Language detected: {detected_language}")
            
            return {
                "text": alternative.transcript.strip(),
                "confidence": alternative.confidence,
                "language": detected_language,
                "duration": 0.0
            }
            
        except Exception as e:
            logger.error(f"Transcription with language detection failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """
        Check if transcription service is available.
        
        Returns:
            True if client is initialized and ready
        """
        return self.client is not None


# Global instance
transcription_service = TranscriptionService()