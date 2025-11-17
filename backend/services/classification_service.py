"""
Classification service using Google Gemini API.
Classifies notes and extracts metadata using AI.
"""

import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai

from backend.core.config import settings
from backend.schemas.note import NoteClassification
from backend.utils.google_api_utils import (
    validate_gemini_api_key,
    parse_gemini_json_response,
    log_api_usage,
    format_gemini_prompt
)

logger = logging.getLogger(__name__)


class ClassificationService:
    """Service for classifying notes and extracting metadata using Gemini."""
    
    def __init__(self):
        """Initialize the classification service."""
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize Gemini model."""
        try:
            if not validate_gemini_api_key():
                logger.warning(
                    "Gemini API key not configured. "
                    "Classification service will not be available."
                )
                return
            
            # Configure Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Initialize model
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"Gemini model initialized: {settings.GEMINI_MODEL}")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {e}")
            self.model = None
    
    async def classify_note(
        self,
        text: str,
        input_type: str = "text"
    ) -> NoteClassification:
        """
        Classify a note and extract metadata.
        
        Args:
            text: Text content to classify
            input_type: Type of input ('text' or 'audio')
            
        Returns:
            NoteClassification object with extracted metadata
        """
        if not self.model:
            error_msg = "Gemini model not initialized"
            logger.error(error_msg)
            log_api_usage("gemini", "classify", False, error_msg)
            raise Exception(error_msg)
        
        try:
            logger.info(f"Starting classification for {len(text)} characters")
            
            # Create prompt
            prompt = self._create_classification_prompt(text, input_type)
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            # Parse response
            response_text = response.text
            logger.debug(f"Gemini response: {response_text[:200]}...")
            
            # Parse JSON from response
            classification_data = parse_gemini_json_response(response_text)
            
            if not classification_data:
                logger.warning("Failed to parse Gemini response as JSON, using fallback")
                return self._create_fallback_classification(text)
            
            # Create NoteClassification object
            classification = NoteClassification(**classification_data)
            
            logger.info(f"Classification completed: {classification.primary_tag}")
            log_api_usage("gemini", "classify", True, f"tag: {classification.primary_tag}")
            
            return classification
            
        except Exception as e:
            error_msg = f"Classification failed: {str(e)}"
            logger.error(error_msg)
            log_api_usage("gemini", "classify", False, error_msg)
            
            # Return fallback classification
            return self._create_fallback_classification(text)
    
    def _create_classification_prompt(self, text: str, input_type: str) -> str:
        """
        Create prompt for Gemini classification.
        
        Args:
            text: Text to classify
            input_type: Type of input
            
        Returns:
            Formatted prompt
        """
        system_instruction = """You are an AI assistant that analyzes notes and extracts structured information.

Analyze the following note and extract information in a JSON format.

IMPORTANT RULES:
1. Return ONLY valid JSON, no other text
2. Do not include markdown code blocks or formatting
3. Be concise and accurate
4. Extract all relevant entities and action items

Categories for primary_tag:
- Work: Professional tasks, meetings, projects
- Personal: Personal life, family, friends
- Travel: Travel plans, destinations, bookings
- Ideas: Creative ideas, brainstorming
- Projects: Personal or professional projects
- Health: Health, fitness, medical
- Learning: Education, courses, learning
- Finance: Money, investments, budgets
- Shopping: Shopping lists, purchases
- Other: Anything else"""
        
        user_input = f"""Note Type: {input_type}
Note Content: {text}

Return JSON with this exact structure:
{{
  "title": "Brief descriptive title (5-10 words)",
  "summary": "2-3 sentence summary",
  "primary_tag": "Work|Personal|Travel|Ideas|Projects|Health|Learning|Finance|Shopping|Other",
  "secondary_tags": ["specific", "topic", "keywords"],
  "key_entities": {{
    "people": ["names of people mentioned"],
    "places": ["locations mentioned"],
    "dates": ["dates or deadlines"],
    "companies": ["organizations mentioned"]
  }},
  "actionable_items": [
    {{
      "task": "specific action to take",
      "deadline": "deadline if mentioned, else null",
      "priority": "high|medium|low"
    }}
  ],
  "topics": ["main", "topics", "discussed"],
  "sentiment": "positive|neutral|negative",
  "priority": "high|medium|low"
}}"""
        
        return f"{system_instruction}\n\n{user_input}"
    
    def _create_fallback_classification(self, text: str) -> NoteClassification:
        """
        Create a basic classification when AI fails.
        
        Args:
            text: Original text
            
        Returns:
            Basic NoteClassification
        """
        logger.warning("Using fallback classification")
        
        # Simple heuristics for fallback
        title = text[:100] if len(text) <= 100 else text[:97] + "..."
        summary = text[:200] if len(text) <= 200 else text[:197] + "..."
        
        return NoteClassification(
            title=title,
            summary=summary,
            primary_tag="Other",
            secondary_tags=[],
            key_entities={"people": [], "places": [], "dates": [], "companies": []},
            actionable_items=[],
            topics=[],
            sentiment="neutral",
            priority="medium"
        )
    
    def is_available(self) -> bool:
        """
        Check if classification service is available.
        
        Returns:
            True if model is initialized and ready
        """
        return self.model is not None


# Global instance
classification_service = ClassificationService()