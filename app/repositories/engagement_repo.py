from sqlalchemy.orm import Session
from .. import models
from typing import List

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
