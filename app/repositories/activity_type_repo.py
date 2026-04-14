from sqlalchemy.orm import Session
from .. import models
from typing import List, Optional

class ActivityTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, activity_type: models.ActivityType):
        self.db.add(activity_type)
        self.db.commit()
        self.db.refresh(activity_type)
        return activity_type

    def get_by_id(self, id: int) -> Optional[models.ActivityType]:
        return self.db.query(models.ActivityType).filter(models.ActivityType.id == id).first()

    def get(self, id: int) -> Optional[models.ActivityType]:
        return self.get_by_id(id)

    def get_by_name(self, name: str):
        return self.db.query(models.ActivityType).filter(models.ActivityType.name == name).first()

    def list_all(self):
        return self.db.query(models.ActivityType).all()

    def delete(self, activity_type: models.ActivityType):
        self.db.delete(activity_type)
        self.db.commit()

    def update(self, activity_type: models.ActivityType):
        self.db.commit()
        self.db.refresh(activity_type)
        return activity_type

