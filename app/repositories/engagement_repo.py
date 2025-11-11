from sqlalchemy.orm import Session
from .. import models
from typing import List, Optional
from datetime import date

class EngagementRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, engagement: models.Engagement):
        self.db.add(engagement)
        self.db.commit()
        self.db.refresh(engagement)
        return engagement

    def list_all(self):
        return self.db.query(models.Engagement).all()

    def heatmap_data(self):
        # return records useful for heatmap (lat, lng, participants, district, village)
        return self.db.query(
            models.Engagement.district,
            models.Engagement.village,
            models.Engagement.lat,
            models.Engagement.lng,
            models.Engagement.participants,
        ).all()

    def list_filtered(self,
                      offset: int = 0,
                      limit: int = 20,
                      district: Optional[str] = None,
                      event_type: Optional[str] = None,
                      date_from: Optional[date] = None,
                      date_to: Optional[date] = None,
                      min_participants: Optional[int] = None):
        q = self.db.query(models.Engagement)
        if district:
            q = q.filter(models.Engagement.district == district)
        if event_type:
            q = q.filter(models.Engagement.event_type == event_type)
        if date_from:
            q = q.filter(models.Engagement.date >= date_from)
        if date_to:
            q = q.filter(models.Engagement.date <= date_to)
        if min_participants:
            q = q.filter(models.Engagement.participants >= min_participants)
        total = q.count()
        items = q.offset(offset).limit(limit).all()
        return items, total
