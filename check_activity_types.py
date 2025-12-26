import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import ActivityType, Event

db = SessionLocal()
try:
    # Get all activity types
    types = db.query(ActivityType).all()
    print("=== Activity Types ===")
    for t in types:
        event_count = db.query(Event).filter(Event.activity_type_id == t.id).count()
        print(f"  {t.id}: {t.name} (max: {t.max_participants}) - Events: {event_count}")
    
    print(f"\nTotal Activity Types: {len(types)}")
    print(f"Total Events: {db.query(Event).count()}")
finally:
    db.close()
