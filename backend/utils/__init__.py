"""Utility functions."""

from backend.utils.file_utils import (
    ensure_directory_exists,
    get_user_audio_directory,
    save_audio_file,
    delete_file,
    validate_audio_file,
    cleanup_temp_files,
)
from backend.utils.audio_utils import (
    convert_audio_format,
    get_audio_duration,
    normalize_audio,
)
from backend.utils.google_api_utils import (
    validate_gemini_api_key,
    validate_speech_to_text_credentials,
    validate_gdrive_credentials,
    validate_all_google_apis,
    get_gdrive_service,
    refresh_gdrive_token,
    handle_google_api_error,
    create_gdrive_oauth_flow,
    format_gemini_prompt,
    parse_gemini_json_response,
    estimate_token_count,
    log_api_usage,
)

__all__ = [
    # File utils
    "ensure_directory_exists",
    "get_user_audio_directory",
    "save_audio_file",
    "delete_file",
    "validate_audio_file",
    "cleanup_temp_files",
    # Audio utils
    "convert_audio_format",
    "get_audio_duration",
    "normalize_audio",
    # Google API utils
    "validate_gemini_api_key",
    "validate_speech_to_text_credentials",
    "validate_gdrive_credentials",
    "validate_all_google_apis",
    "get_gdrive_service",
    "refresh_gdrive_token",
    "handle_google_api_error",
    "create_gdrive_oauth_flow",
    "format_gemini_prompt",
    "parse_gemini_json_response",
    "estimate_token_count",
    "log_api_usage",
]