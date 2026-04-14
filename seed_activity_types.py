
import sys
import os

# Add current directory to sys.path to safely import from app
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.database import SessionLocal
from app.models import ActivityType, Event, Attendee

def seed_activity_types():
    db = SessionLocal()
    try:
        print("Seeding Activity Types...")
        
        # Clear existing data with cascade logic
        # Delete Attendees first (depend on Events)
        print("Clearing existing Attendees...")
        db.query(Attendee).delete()
        
        # Delete Events (depend on ActivityType)
        print("Clearing existing Events...")
        db.query(Event).delete()
        
        # Delete Activity Types
        print("Clearing existing Activity Types...")
        db.query(ActivityType).delete()
        
        db.commit()
        print("Existing data cleared.")
        
        ACTIVITY_TYPES = [
            {"name": "Reses", "max_participants": 150},
            {"name": "Pengawasan Penyelenggaraan Pemerintah", "max_participants": 100},
            {"name": "Pendidikan Demokrasi", "max_participants": 50},
            {"name": "Dialog Wakil Rakyat", "max_participants": 100},
            {"name": "Sapa Budaya", "max_participants": 100},
        ]
        
        created_count = 0
        
        for activity_data in ACTIVITY_TYPES:
            print(f"  Creating Activity '{activity_data['name']}'...")
            new_activity = ActivityType(
                name=activity_data['name'],
                max_participants=activity_data['max_participants']
            )
            db.add(new_activity)
            created_count += 1
        
        db.commit()
        print(f"\nSeeding Complete!")
        print(f"Created: {created_count}")
        
    except Exception as e:
        print(f"Error seeding activity types: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_activity_types()
