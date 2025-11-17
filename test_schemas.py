"""Test schemas and utilities."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_schemas():
    """Test Pydantic schemas."""
    print("Testing Pydantic schemas...")
    
    try:
        from backend.schemas.note import NoteCreate, NoteResponse
        from backend.schemas.query import SearchRequest, InsightRequest
        from backend.schemas.telegram import TelegramUpdate
        
        # Test NoteCreate
        note = NoteCreate(
            input_type="text",
            source="web",
            original_text="Test note",
            user_id="test_user"
        )
        print(f"✅ NoteCreate: {note.input_type}")
        
        # Test SearchRequest
        search = SearchRequest(query="test", page=1, page_size=10)
        print(f"✅ SearchRequest: {search.query}")
        
        print("✅ All schemas working!")
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False


def test_utils():
    """Test utility functions."""
    print("\nTesting utilities...")
    
    try:
        from backend.utils.file_utils import ensure_directory_exists, get_unique_filename
        from backend.utils.google_api_utils import (
            validate_all_google_apis,
            parse_gemini_json_response,
            estimate_token_count
        )
        
        # Test directory creation
        ensure_directory_exists("./data/test")
        print("✅ Directory creation works")
        
        # Test unique filename
        filename = get_unique_filename("test.mp3", "user123")
        print(f"✅ Unique filename: {filename}")
        
        # Test Google API validation
        api_status = validate_all_google_apis()
        print(f"✅ Google API validation: {api_status}")
        
        # Test JSON parsing
        test_json = '```json\n{"test": "value"}\n```'
        parsed = parse_gemini_json_response(test_json)
        print(f"✅ JSON parsing: {parsed}")
        
        # Test token estimation
        tokens = estimate_token_count("This is a test sentence")
        print(f"✅ Token estimation: {tokens} tokens")
        
        print("✅ All utilities working!")
        return True
        
    except Exception as e:
        print(f"❌ Utility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*50)
    print("TESTING SCHEMAS AND UTILITIES")
    print("="*50)
    
    if not test_schemas():
        sys.exit(1)
    
    if not test_utils():
        sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED!")
    print("="*50)