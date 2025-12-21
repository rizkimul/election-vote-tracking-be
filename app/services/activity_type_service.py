from fastapi import HTTPException
from .. import models, schemas
from ..repositories.activity_type_repo import ActivityTypeRepository

class ActivityTypeService:
    def __init__(self, repo: ActivityTypeRepository):
        self.repo = repo

    def create_activity_type(self, data: schemas.ActivityTypeCreate):
        # Check if exists
        existing = self.repo.get_by_name(data.name)
        if existing:
            return existing
        obj = models.ActivityType(**data.dict())
        return self.repo.create(obj)

    def list_activity_types(self):
        return self.repo.list_all()

    def delete_activity_type(self, activity_type_id: int):
        activity_type = self.repo.get_by_id(activity_type_id)
        if not activity_type:
            raise HTTPException(status_code=404, detail="Activity type not found")
        self.repo.delete(activity_type)
        return {"message": "Activity type deleted successfully"}

