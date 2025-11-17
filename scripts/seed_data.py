"""
Seed database with sample data for testing.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.database import SessionLocal
from backend.models.user import User
from backend.models.note import Note
import uuid

def seed_data():
    """Add sample data to database."""
    
    print("="*50)
    print("SEEDING DATABASE WITH SAMPLE DATA")
    print("="*50)
    
    db = SessionLocal()
    
    try:
        # Create test user
        print("\n1. Creating test user...")
        test_user = User(
            id="test_user_001",
            telegram_id="123456789",
            telegram_username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            language_preference="en"
        )
        
        db.add(test_user)
        db.commit()
        print("✅ Test user created: test_user_001")
        
        # Create sample notes
        print("\n2. Creating sample notes...")
        
        sample_notes = [
            {
                "input_type": "text",
                "source": "web",
                "original_text": "Team meeting scheduled for next Monday at 10 AM to discuss Q4 strategy and goals.",
                "title": "Q4 Strategy Meeting",
                "summary": "Team meeting scheduled for Monday to discuss Q4 plans.",
                "primary_tag": "Work",
                "secondary_tags": ["meeting", "strategy", "Q4"],
                "actionable_items": [{"task": "Attend Q4 meeting", "deadline": "Monday 10 AM", "priority": "high"}],
                "sentiment": "neutral",
                "priority": "high"
            },
            {
                "input_type": "text",
                "source": "telegram",
                "original_text": "Don't forget to buy groceries: milk, eggs, bread, and coffee.",
                "title": "Grocery Shopping List",
                "summary": "Need to buy milk, eggs, bread, and coffee.",
                "primary_tag": "Personal",
                "secondary_tags": ["shopping", "groceries"],
                "actionable_items": [{"task": "Buy groceries", "deadline": None, "priority": "medium"}],
                "sentiment": "neutral",
                "priority": "medium"
            },
            {
                "input_type": "text",
                "source": "web",
                "original_text": "Idea for new mobile app: A habit tracker that uses AI to provide personalized motivation and insights.",
                "title": "AI-Powered Habit Tracker App Idea",
                "summary": "Mobile app idea combining habit tracking with AI-powered personalized motivation.",
                "primary_tag": "Ideas",
                "secondary_tags": ["app", "AI", "mobile", "habits"],
                "actionable_items": [],
                "sentiment": "positive",
                "priority": "low"
            },
            {
                "input_type": "text",
                "source": "web",
                "original_text": "Planning trip to Japan in Spring 2025. Want to visit Tokyo, Kyoto, and Osaka. Budget around $3000.",
                "title": "Japan Trip Planning",
                "summary": "Planning a Spring 2025 trip to Japan covering Tokyo, Kyoto, and Osaka with $3000 budget.",
                "primary_tag": "Travel",
                "secondary_tags": ["Japan", "vacation", "planning"],
                "key_entities": {
                    "places": ["Tokyo", "Kyoto", "Osaka", "Japan"],
                    "dates": ["Spring 2025"],
                    "companies": [],
                    "people": []
                },
                "actionable_items": [{"task": "Research Japan travel", "deadline": None, "priority": "low"}],
                "sentiment": "positive",
                "priority": "medium"
            },
            {
                "input_type": "text",
                "source": "telegram",
                "original_text": "Started learning Python data science. Completed first 3 modules on Coursera. Very interesting!",
                "title": "Python Data Science Progress",
                "summary": "Started learning Python data science on Coursera, completed 3 modules.",
                "primary_tag": "Learning",
                "secondary_tags": ["python", "data science", "coursera"],
                "actionable_items": [],
                "sentiment": "positive",
                "priority": "low"
            }
        ]
        
        created_count = 0
        for note_data in sample_notes:
            note = Note(
                user_id="test_user_001",
                input_type=note_data["input_type"],
                source=note_data["source"],
                original_text=note_data["original_text"],
                title=note_data["title"],
                summary=note_data["summary"],
                primary_tag=note_data["primary_tag"],
                secondary_tags=note_data.get("secondary_tags", []),
                key_entities=note_data.get("key_entities", {}),
                actionable_items=note_data.get("actionable_items", []),
                sentiment=note_data["sentiment"],
                priority=note_data["priority"],
                processing_status="completed",
                created_at=datetime.utcnow() - timedelta(days=created_count)
            )
            
            db.add(note)
            created_count += 1
        
        db.commit()
        print(f"✅ Created {created_count} sample notes")
        
        print("\n" + "="*50)
        print("✅ SAMPLE DATA SEEDED SUCCESSFULLY!")
        print("="*50)
        print("\n📝 Test User Credentials:")
        print("   User ID: test_user_001")
        print("   Telegram ID: 123456789")
        print(f"   Sample Notes: {created_count}")
        print("\n💡 Use these in the Streamlit app to test features!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = seed_data()
    sys.exit(0 if success else 1)