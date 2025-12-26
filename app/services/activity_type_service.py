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
            raise HTTPException(status_code=404, detail="Jenis kegiatan tidak ditemukan")
        self.repo.delete(activity_type)
        return {"message": "Jenis kegiatan berhasil dihapus"}

    def update_activity_type(self, activity_type_id: int, data: schemas.ActivityTypeCreate):
        activity_type = self.repo.get_by_id(activity_type_id)
        if not activity_type:
            raise HTTPException(status_code=404, detail="Jenis kegiatan tidak ditemukan")
        
        # Update fields
        activity_type.name = data.name
        activity_type.max_participants = data.max_participants
        
        return self.repo.update(activity_type)

