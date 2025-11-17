"""
Insight service for generating AI-powered insights and summaries.
Uses Gemini API to analyze collections of notes.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import google.generativeai as genai

from backend.models.note import Note
from backend.core.config import settings
from backend.schemas.query import InsightRequest, InsightResponse
from backend.utils.google_api_utils import log_api_usage

logger = logging.getLogger(__name__)


class InsightService:
    """Service for generating insights from notes."""
    
    def __init__(self):
        """Initialize insight service."""
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Gemini model."""
        try:
            if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("Gemini model initialized for insights")
        except Exception as e:
            logger.error(f"Error initializing Gemini for insights: {e}")
    
    async def generate_insights(
        self,
        db: Session,
        user_id: str,
        insight_request: InsightRequest
    ) -> InsightResponse:
        """
        Generate insights based on user's notes.
        
        Args:
            db: Database session
            user_id: User ID
            insight_request: Insight request parameters
            
        Returns:
            InsightResponse with AI-generated insights
        """
        try:
            logger.info(f"Generating insights for user {user_id}: {insight_request.query}")
            
            # Fetch relevant notes
            notes = await self._fetch_relevant_notes(db, user_id, insight_request)
            
            if not notes:
                return InsightResponse(
                    query=insight_request.query,
                    insight="No notes found matching your criteria.",
                    notes_analyzed=0,
                    related_notes=[],
                    summary_points=[],
                    action_items=[]
                )
            
            # Generate insights using Gemini
            if self.model:
                insight_text, summary_points, action_items = await self._generate_ai_insights(
                    notes,
                    insight_request.query
                )
            else:
                # Fallback to basic insights
                insight_text, summary_points, action_items = self._generate_basic_insights(notes)
            
            # Get note IDs
            note_ids = [str(note.id) for note in notes[:10]]  # Limit to top 10
            
            logger.info(f"Insights generated from {len(notes)} notes")
            
            return InsightResponse(
                query=insight_request.query,
                insight=insight_text,
                notes_analyzed=len(notes),
                related_notes=note_ids,
                summary_points=summary_points,
                action_items=action_items
            )
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            raise
    
    async def _fetch_relevant_notes(
        self,
        db: Session,
        user_id: str,
        insight_request: InsightRequest
    ) -> List[Note]:
        """Fetch notes relevant to the insight request."""
        
        query = db.query(Note).filter(
            Note.user_id == user_id,
            Note.processing_status == "completed"
        )
        
        # Apply filters
        if insight_request.primary_tag:
            query = query.filter(Note.primary_tag == insight_request.primary_tag)
        
        if insight_request.start_date:
            query = query.filter(Note.created_at >= insight_request.start_date)
        
        if insight_request.end_date:
            query = query.filter(Note.created_at <= insight_request.end_date)
        
        # Order by date
        query = query.order_by(Note.created_at.desc())
        
        # Limit
        query = query.limit(insight_request.max_notes)
        
        return query.all()
    
    async def _generate_ai_insights(
        self,
        notes: List[Note],
        query: str
    ) -> tuple[str, List[str], List[str]]:
        """Generate insights using Gemini AI."""
        
        try:
            # Prepare notes summary for AI
            notes_summary = self._prepare_notes_for_ai(notes)
            
            # Create prompt
            prompt = f"""You are an AI assistant analyzing personal notes to provide insights.

User Query: {query}

Notes to analyze ({len(notes)} notes):
{notes_summary}

Please provide:
1. A comprehensive insight answering the user's query (2-3 paragraphs)
2. Key summary points (3-5 bullet points)
3. Action items extracted from the notes (if any)

Format your response as:

INSIGHT:
[Your comprehensive insight here]

SUMMARY POINTS:
- Point 1
- Point 2
- Point 3

ACTION ITEMS:
- Action 1
- Action 2
"""
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                }
            )
            
            # Parse response
            insight_text, summary_points, action_items = self._parse_insight_response(
                response.text
            )
            
            log_api_usage("gemini", "generate_insights", True, f"{len(notes)} notes")
            
            return insight_text, summary_points, action_items
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            log_api_usage("gemini", "generate_insights", False, str(e))
            return self._generate_basic_insights(notes)
    
    def _prepare_notes_for_ai(self, notes: List[Note]) -> str:
        """Prepare notes summary for AI analysis."""
        
        notes_text = []
        for i, note in enumerate(notes[:20], 1):  # Limit to 20 for context window
            text_content = note.get_text_content()
            notes_text.append(
                f"[Note {i}] {note.created_at.strftime('%Y-%m-%d')} - "
                f"{note.primary_tag}: {text_content[:200]}"
            )
        
        return "\n".join(notes_text)
    
    def _parse_insight_response(self, response_text: str) -> tuple[str, List[str], List[str]]:
        """Parse Gemini response into structured format."""
        
        try:
            parts = response_text.split("SUMMARY POINTS:")
            insight_part = parts[0].replace("INSIGHT:", "").strip()
            
            if len(parts) > 1:
                remaining = parts[1].split("ACTION ITEMS:")
                summary_part = remaining[0].strip()
                action_part = remaining[1].strip() if len(remaining) > 1 else ""
                
                # Extract bullet points
                summary_points = [
                    line.strip().lstrip("-•").strip()
                    for line in summary_part.split("\n")
                    if line.strip() and line.strip().startswith(("-", "•", "*"))
                ]
                
                action_items = [
                    line.strip().lstrip("-•").strip()
                    for line in action_part.split("\n")
                    if line.strip() and line.strip().startswith(("-", "•", "*"))
                ]
            else:
                summary_points = []
                action_items = []
            
            return insight_part, summary_points, action_items
            
        except Exception as e:
            logger.error(f"Error parsing insight response: {e}")
            return response_text, [], []
    
    def _generate_basic_insights(self, notes: List[Note]) -> tuple[str, List[str], List[str]]:
        """Generate basic insights without AI."""
        
        # Count by tag
        tag_counts = {}
        all_action_items = []
        
        for note in notes:
            tag = note.primary_tag or "Other"
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            if note.actionable_items:
                all_action_items.extend([
                    item.get("task", "") for item in note.actionable_items
                ])
        
        # Create basic insight
        insight = f"Analyzed {len(notes)} notes. "
        insight += f"Most common categories: {', '.join(sorted(tag_counts.keys()))}. "
        insight += f"Found {len(all_action_items)} action items across your notes."
        
        summary_points = [
            f"Total notes analyzed: {len(notes)}",
            f"Date range: {notes[-1].created_at.strftime('%Y-%m-%d')} to {notes[0].created_at.strftime('%Y-%m-%d')}",
            f"Categories: {', '.join(tag_counts.keys())}"
        ]
        
        return insight, summary_points, all_action_items[:5]


# Global instance
insight_service = InsightService()