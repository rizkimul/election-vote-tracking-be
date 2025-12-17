from sqlalchemy.orm import Session
from .. import models
from typing import List, Optional

class AttendeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, attendee: models.Attendee):
        self.db.add(attendee)
        self.db.commit()
        self.db.refresh(attendee)
        return attendee

    def get_by_event_and_nik(self, event_id: int, nik: str):
        return self.db.query(models.Attendee).filter(
            models.Attendee.event_id == event_id,
            models.Attendee.nik == nik
        ).first()

    def list_by_event(self, event_id: int, offset: int = 0, limit: int = 50):
        q = self.db.query(models.Attendee).filter(models.Attendee.event_id == event_id)
        return q.offset(offset).limit(limit).all()

    def count_by_event(self, event_id: int):
        return self.db.query(models.Attendee).filter(models.Attendee.event_id == event_id).count()
