from typing import List
from .. import models, schemas

class EngagementService:
    def __init__(self, engagement_repo):
        self.engagement_repo = engagement_repo

    def add_engagement(self, data: schemas.EngagementCreate):
        ent = models.Engagement(**data.dict())
        return self.engagement_repo.create(ent)

    def list_engagements(self):
        return self.engagement_repo.list_all()

    def heatmap(self):
        return self.engagement_repo.heatmap_data()
