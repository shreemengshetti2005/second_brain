"""
Database setup script.
Creates all tables and initializes the database.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# CRITICAL: Import models BEFORE init_db
from backend.models import User, Note  # Import models first!
from backend.core.database import init_db, check_db_connection, engine
from backend.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """Setup database tables."""
    
    print("="*50)
    print("DATABASE SETUP")
    print("="*50)
    
    # Check connection
    print("\n1. Checking database connection...")
    if not check_db_connection():
        print("❌ Cannot connect to database!")
        print(f"   Connection string: {settings.DATABASE_URL}")
        print("\nPlease ensure:")
        print("  - PostgreSQL is running")
        print("  - Database 'secondbrain' exists")
        print("  - Connection details in .env are correct")
        return False
    
    print("✅ Database connection successful")
    
    # Create tables
    print("\n2. Creating database tables...")
    try:
        init_db()
        print("✅ Tables created successfully")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"\n📊 Created tables:")
            for table in tables:
                print(f"   - {table}")
        else:
            print("⚠️  No tables found (might be normal if already created)")
        
        print("\n" + "="*50)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)