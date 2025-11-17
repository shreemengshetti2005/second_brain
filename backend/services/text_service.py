"""
Text service for handling direct text input processing.
Validates and prepares text notes.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TextService:
    """Service for text note processing."""
    
    async def process_text_input(
        self,
        text: str,
        user_id: str,
        source: str = "web"
    ) -> Dict[str, Any]:
        """
        Process text input.
        
        Args:
            text: Text content
            user_id: User ID
            source: Source of input (web, telegram, api)
            
        Returns:
            Dictionary with processed text info
        """
        try:
            logger.info(f"Processing text input for user {user_id} from {source}")
            
            # Clean and validate text
            cleaned_text = self._clean_text(text)
            
            # Validate
            is_valid, error_msg = self.validate_text(cleaned_text)
            if not is_valid:
                logger.error(f"Text validation failed: {error_msg}")
                raise ValueError(error_msg)
            
            # Calculate stats
            word_count = len(cleaned_text.split())
            char_count = len(cleaned_text)
            
            logger.info(
                f"Text processed: {word_count} words, {char_count} characters"
            )
            
            return {
                "text": cleaned_text,
                "word_count": word_count,
                "char_count": char_count,
                "source": source
            }
            
        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean text input.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        cleaned = " ".join(text.split())
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def validate_text(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Validate text input.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if text is empty
        if not text or len(text.strip()) == 0:
            return False, "Text cannot be empty"
        
        # Check minimum length
        if len(text) < 3:
            return False, "Text is too short (minimum 3 characters)"
        
        # Check maximum length (100,000 characters)
        if len(text) > 100000:
            return False, "Text is too long (maximum 100,000 characters)"
        
        return True, None
    
    def extract_hashtags(self, text: str) -> list[str]:
        """
        Extract hashtags from text.
        
        Args:
            text: Text containing hashtags
            
        Returns:
            List of hashtags without # symbol
        """
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return list(set(hashtags))  # Remove duplicates
    
    def extract_mentions(self, text: str) -> list[str]:
        """
        Extract @mentions from text.
        
        Args:
            text: Text containing mentions
            
        Returns:
            List of mentions without @ symbol
        """
        import re
        mentions = re.findall(r'@(\w+)', text)
        return list(set(mentions))


# Global instance
text_service = TextService()