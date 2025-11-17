"""
AI-powered classification service using Google Gemini.
Clean, merged and corrected version.
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
)

logger = logging.getLogger(__name__)


class ClassificationService:
    """Service for classifying notes and extracting metadata using Gemini."""
    
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize Gemini model."""
        try:
            if not validate_gemini_api_key():
                logger.warning("Gemini API key not configured.")
                return

            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"Gemini model initialized: {settings.GEMINI_MODEL}")
            
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {e}")
            self.model = None
    
    async def classify_note(self, text: str, input_type: str = "text") -> NoteClassification:
        """
        Classify a note and extract metadata using Gemini.
        """
        if not self.model:
            msg = "Gemini model not initialized"
            log_api_usage("gemini", "classify", False, msg)
            return self._create_fallback_classification(text)

        try:
            logger.info(f"Classifying note ({len(text)} chars)")

            prompt = self._build_prompt(text, input_type)

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )

            response_text = self._clean_response_text(response.text)

            # Parse JSON
            classification_data = parse_gemini_json_response(response_text)

            if not classification_data:
                # Try manual JSON parse before fallback
                try:
                    classification_data = json.loads(response_text)
                except:
                    logger.error("Failed to parse Gemini JSON. Using fallback.")
                    return self._create_fallback_classification(text)

            # Build Pydantic model
            classification = NoteClassification(
                title=classification_data.get("title", text[:50]),
                summary=classification_data.get("summary", text[:200]),
                primary_tag=classification_data.get("primary_tag", "Other"),
                secondary_tags=classification_data.get("secondary_tags", []),
                key_entities=classification_data.get("key_entities", {}),
                actionable_items=classification_data.get("actionable_items", []),
                topics=classification_data.get("topics", []),
                sentiment=classification_data.get("sentiment", "neutral"),
                priority=classification_data.get("priority", "medium")
            )

            log_api_usage("gemini", "classify", True, f"tag: {classification.primary_tag}")
            return classification

        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return self._create_fallback_classification(text)

    # ----------------------------------------------------------------------
    # Helper: Build Prompt
    # ----------------------------------------------------------------------

    def _build_prompt(self, text: str, input_type: str) -> str:
        return f"""
You are an AI assistant that analyzes notes and extracts structured metadata.

Analyze the following note and return ONLY valid JSON.

Note Type: {input_type}
Note Content: "{text}"

Return exactly this structure:

{{
  "title": "5-10 word title",
  "summary": "1-2 sentence summary",
  "primary_tag": "Work|Personal|Travel|Ideas|Projects|Health|Learning|Finance|Shopping|Other",
  "secondary_tags": ["tag1", "tag2", "tag3"],
  "key_entities": {{
    "people": [],
    "places": [],
    "dates": [],
    "companies": []
  }},
  "actionable_items": [
    {{
      "task": "",
      "deadline": null,
      "priority": "high|medium|low"
    }}
  ],
  "topics": ["topic1", "topic2"],
  "sentiment": "positive|neutral|negative",
  "priority": "high|medium|low"
}}

RULES:
- Return ONLY JSON. No markdown. No explanation.
- If no action items → use empty array [].
- Choose tags carefully.
- Prioritize correctness and clean JSON.
"""

    # ----------------------------------------------------------------------
    # Helper: Clean Gemini Response
    # ----------------------------------------------------------------------

    def _clean_response_text(self, text: str) -> str:
        """Remove markdown code blocks and trim text."""
        cleaned = text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return cleaned.strip()

    # ----------------------------------------------------------------------
    # Fallback Logic
    # ----------------------------------------------------------------------

    def _create_fallback_classification(self, text: str) -> NoteClassification:
        """Keyword-based fallback classification."""
        logger.warning("Using fallback classification")

        text_lower = text.lower()

        category_keywords = {
            "Work": ["meeting", "project", "deadline", "client", "email"],
            "Personal": ["family", "friend", "home", "birthday"],
            "Travel": ["flight", "trip", "airport", "hotel"],
            "Ideas": ["idea", "brainstorm", "concept"],
            "Projects": ["build", "develop", "launch"],
            "Health": ["doctor", "gym", "exercise", "medicine"],
            "Learning": ["learn", "study", "course", "tutorial"],
            "Finance": ["budget", "expense", "bank", "invoice"],
            "Shopping": ["buy", "order", "groceries"],
        }

        primary_tag = "Other"
        for cat, keywords in category_keywords.items():
            if any(k in text_lower for k in keywords):
                primary_tag = cat
                break

        # Priority detection
        urgency_words = ["urgent", "asap", "immediately", "critical"]
        low_words = ["maybe", "someday"]

        if any(k in text_lower for k in urgency_words):
            priority = "high"
        elif any(k in text_lower for k in low_words):
            priority = "low"
        else:
            priority = "medium"

        # Simple action extraction
        action_keywords = ["need to", "have to", "must", "should"]
        actionable_items = []
        if any(k in text_lower for k in action_keywords):
            actionable_items.append({
                "task": text[:100],
                "deadline": None,
                "priority": priority
            })

        return NoteClassification(
            title=text[:60],
            summary=text[:150],
            primary_tag=primary_tag,
            secondary_tags=[],
            key_entities={"people": [], "places": [], "dates": [], "companies": []},
            actionable_items=actionable_items,
            topics=[],
            sentiment="neutral",
            priority=priority
        )

    def is_available(self) -> bool:
        return self.model is not None


# Global service instance
classification_service = ClassificationService()
