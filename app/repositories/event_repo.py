from sqlalchemy.orm import Session
from .. import models
from typing import List, Optional
from datetime import date

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, event: models.Event):
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_filtered(self,
                      offset: int = 0,
                      limit: int = 20,
                      dapil: Optional[str] = None,
                      date_from: Optional[date] = None,
                      date_to: Optional[date] = None,
                      activity_type_id: Optional[int] = None):
        q = self.db.query(models.Event)
        if dapil:
            q = q.filter(models.Event.dapil == dapil)
        if activity_type_id:
            q = q.filter(models.Event.activity_type_id == activity_type_id)
        if date_from:
            q = q.filter(models.Event.date >= date_from)
        if date_to:
            q = q.filter(models.Event.date <= date_to)
        
        total = q.count()
        total = q.count()
        items = q.offset(offset).limit(limit).all()
        return items, total

    def get(self, id: int) -> Optional[models.Event]:
        return self.db.query(models.Event).get(id)

    def update(self, event: models.Event, data: dict):
        for key, value in data.items():
            setattr(event, key, value)
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, event: models.Event):
        self.db.delete(event)
        self.db.commit()

