
import sys
import os
from sqlalchemy import func

# Add current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.database import SessionLocal
from app.models import Event, Attendee

def verify():
    db = SessionLocal()
    try:
        event_count = db.query(func.count(Event.id)).scalar()
        attendee_count = db.query(func.count(Attendee.id)).scalar()
        print(f"Events: {event_count}")
        print(f"Attendees: {attendee_count}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
