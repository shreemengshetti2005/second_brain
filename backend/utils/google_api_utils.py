"""
Utility functions for Google Cloud APIs.
Helper functions for authentication, error handling, and common operations.
"""

import os
import logging
from typing import Optional, Dict, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.core.config import settings

logger = logging.getLogger(__name__)


def validate_gemini_api_key() -> bool:
    """
    Validate that Gemini API key is configured.
    
    Returns:
        True if API key is configured, False otherwise
    """
    if not settings.GEMINI_API_KEY:
        logger.error("Gemini API key is not configured")
        return False
    
    if settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        logger.error("Gemini API key is still set to default value")
        return False
    
    return True


def validate_speech_to_text_credentials() -> bool:
    """
    Validate that Speech-to-Text credentials are configured.
    
    Returns:
        True if credentials are configured, False otherwise
    """
    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        logger.error("Google Application Credentials not configured")
        return False
    
    if not os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
        logger.error(f"Credentials file not found: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
        return False
    
    return True


def validate_gdrive_credentials() -> bool:
    """
    Validate that Google Drive credentials are configured.
    
    Returns:
        True if credentials are configured, False otherwise
    """
    if not settings.GDRIVE_CLIENT_ID or not settings.GDRIVE_CLIENT_SECRET:
        logger.error("Google Drive credentials not configured")
        return False
    
    if settings.GDRIVE_CLIENT_ID == "your_client_id.apps.googleusercontent.com":
        logger.error("Google Drive credentials are still set to default values")
        return False
    
    return True


def get_gdrive_service(credentials: Credentials):
    """
    Get authenticated Google Drive service.
    
    Args:
        credentials: Google OAuth2 credentials
        
    Returns:
        Google Drive service object
    """
    try:
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Error creating Drive service: {e}")
        raise


def refresh_gdrive_token(token_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Refresh Google Drive OAuth token.
    
    Args:
        token_data: Dictionary containing token information
        
    Returns:
        Updated token data or None if refresh failed
    """
    try:
        credentials = Credentials.from_authorized_user_info(token_data)
        
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            
            # Convert back to dict
            return {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
        
        return token_data
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return None


def handle_google_api_error(error: HttpError) -> str:
    """
    Handle Google API errors and return user-friendly message.
    
    Args:
        error: HttpError from Google API
        
    Returns:
        User-friendly error message
    """
    error_code = error.resp.status
    
    error_messages = {
        400: "Bad request. Please check your input.",
        401: "Authentication failed. Please re-authenticate.",
        403: "Access denied. Check your permissions.",
        404: "Resource not found.",
        429: "Rate limit exceeded. Please try again later.",
        500: "Google API server error. Please try again later.",
        503: "Service temporarily unavailable. Please try again later."
    }
    
    message = error_messages.get(error_code, f"API error: {error_code}")
    logger.error(f"Google API error: {message} - {error}")
    
    return message


def create_gdrive_oauth_flow():
    """
    Create Google Drive OAuth flow for user authentication.
    
    Returns:
        OAuth flow object
    """
    try:
        # Scopes required for Google Drive
        scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.metadata.readonly'
        ]
        
        # Create flow
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": settings.GDRIVE_CLIENT_ID,
                    "client_secret": settings.GDRIVE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GDRIVE_REDIRECT_URI]
                }
            },
            scopes=scopes
        )
        
        return flow
        
    except Exception as e:
        logger.error(f"Error creating OAuth flow: {e}")
        raise


def format_gemini_prompt(system_instruction: str, user_input: str) -> str:
    """
    Format prompt for Gemini API.
    
    Args:
        system_instruction: System-level instruction
        user_input: User's input text
        
    Returns:
        Formatted prompt
    """
    return f"""{system_instruction}

User Input:
{user_input}

Response:"""


def parse_gemini_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON response from Gemini, handling markdown code blocks.
    
    Args:
        response_text: Raw response text from Gemini
        
    Returns:
        Parsed JSON as dictionary or None if parsing failed
    """
    import json
    
    try:
        # Remove markdown code blocks if present
        cleaned_text = response_text.strip()
        
        # Remove ```json and ``` markers
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]  # Remove ```json
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]  # Remove ```
        
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]  # Remove trailing ```
        
        cleaned_text = cleaned_text.strip()
        
        # Parse JSON
        return json.loads(cleaned_text)
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from Gemini response: {e}")
        logger.error(f"Response text: {response_text}")
        return None


def estimate_token_count(text: str) -> int:
    """
    Estimate token count for text (rough approximation).
    Uses ~4 characters per token as estimate.
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def check_api_quota(service_name: str) -> Dict[str, Any]:
    """
    Check API quota status (placeholder for future implementation).
    
    Args:
        service_name: Name of the Google service
        
    Returns:
        Dictionary with quota information
    """
    # This is a placeholder - actual implementation would query Google Cloud APIs
    return {
        "service": service_name,
        "status": "unknown",
        "message": "Quota checking not implemented yet"
    }


def validate_all_google_apis() -> Dict[str, bool]:
    """
    Validate all Google API configurations.
    
    Returns:
        Dictionary with validation results for each API
    """
    results = {
        "gemini": validate_gemini_api_key(),
        "speech_to_text": validate_speech_to_text_credentials(),
        "google_drive": validate_gdrive_credentials()
    }
    
    return results


def log_api_usage(api_name: str, operation: str, success: bool, details: Optional[str] = None):
    """
    Log API usage for monitoring and debugging.
    
    Args:
        api_name: Name of the API (gemini, speech_to_text, drive)
        operation: Operation performed (transcribe, classify, upload, etc.)
        success: Whether the operation was successful
        details: Optional additional details
    """
    status = "SUCCESS" if success else "FAILED"
    log_message = f"API Usage: {api_name} - {operation} - {status}"
    
    if details:
        log_message += f" - {details}"
    
    if success:
        logger.info(log_message)
    else:
        logger.error(log_message)