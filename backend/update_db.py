"""
Script to update demo_requests table to add password_hash column
and update the database schema.
"""

from sqlalchemy import text
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models import factory, user, complience_event, product, batch, demo_request

def update_database():
    """Add password_hash column to demo_requests table"""
    db = SessionLocal()
    
    try:
        # Check if column exists
        result = db.execute(text("PRAGMA table_info(demo_requests)"))
        columns = [row[1] for row in result]
        
        if 'password_hash' not in columns:
            print("Adding password_hash column to demo_requests table...")
            db.execute(text("ALTER TABLE demo_requests ADD COLUMN password_hash VARCHAR"))
            db.commit()
            print("✅ Column added successfully!")
        else:
            print("✅ password_hash column already exists")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Updating database schema...")
    update_database()
    print("\nDatabase update complete!")
