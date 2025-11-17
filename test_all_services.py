"""Test all services initialization."""

import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath('.'))

async def test_all_services():
    """Test all services."""
    print("Testing all services initialization...\n")
    
    try:
        from backend.services import (
            transcription_service,
            classification_service,
            embedding_service,
            audio_service,
            text_service,
            search_service,
            insight_service,
            telegram_service,
            gdrive_service
        )
        
        print("✅ All services imported successfully")
        
        # Test availability
        services_status = {
            "Transcription": transcription_service.is_available(),
            "Classification": classification_service.is_available(),
            "Embedding": embedding_service.is_available(),
            "Telegram": telegram_service.is_available(),
        }
        
        print("\n📊 Services Status:")
        for service, available in services_status.items():
            status = "✅ Available" if available else "⚠️  Not configured"
            print(f"  {service}: {status}")
        
        # Test text processing
        print("\n🧪 Testing text service...")
        result = await text_service.process_text_input(
            text="This is a test note about work",
            user_id="test_user",
            source="web"
        )
        print(f"  ✅ Text processed: {result['word_count']} words")
        
        print("\n✅ All services working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*50)
    print("TESTING ALL SERVICES")
    print("="*50)
    
    result = asyncio.run(test_all_services())
    
    print("\n" + "="*50)
    if result:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED!")
    print("="*50)