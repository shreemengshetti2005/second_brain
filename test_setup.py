"""
Test script to verify basic setup is working.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Test if all imports work."""
    print("Testing imports...")
    
    try:
        from backend.core.config import settings
        print(f"✅ Config loaded: {settings.APP_NAME}")
        
        from backend.core.database import Base, engine
        print("✅ Database module loaded")
        
        from backend.models.user import User
        from backend.models.note import Note
        print("✅ Models loaded")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_database_models():
    """Test if database models are defined correctly."""
    print("\nTesting database models...")
    
    try:
        from backend.models.user import User
        from backend.models.note import Note
        from backend.core.database import Base
        
        # Check tables
        tables = Base.metadata.tables.keys()
        print(f"✅ Tables defined: {list(tables)}")
        
        # Check User columns
        user_columns = [c.name for c in User.__table__.columns]
        print(f"✅ User columns: {user_columns}")
        
        # Check Note columns
        note_columns = [c.name for c in Note.__table__.columns]
        print(f"✅ Note columns: {note_columns}")
        
        print("\n✅ Database models are correctly defined!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False


if __name__ == "__main__":
    print("="*50)
    print("TESTING BASIC SETUP")
    print("="*50)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test models
    if not test_database_models():
        sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED!")
    print("="*50)