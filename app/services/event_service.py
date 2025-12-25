from .. import models, schemas
from ..repositories.event_repo import EventRepository
from ..repositories.attendee_repo import AttendeeRepository
from ..repositories.activity_type_repo import ActivityTypeRepository
from datetime import date
from fastapi import HTTPException

class EventService:
    def __init__(self, 
                 event_repo: EventRepository, 
                 attendee_repo: AttendeeRepository,
                 activity_repo: ActivityTypeRepository):
        self.event_repo = event_repo
        self.attendee_repo = attendee_repo
        self.activity_repo = activity_repo

    def create_event(self, data: schemas.EventCreate):
        # Validate activity type exists
        # (SQLAlchemy would fail on FK but explicit check is nice)
        obj = models.Event(**data.dict())
        return self.event_repo.create(obj)

    def list_events(self, page=1, size=20, **kwargs):
        offset = (page - 1) * size
        items, total = self.event_repo.list_filtered(offset=offset, limit=size, **kwargs)
        items, total = self.event_repo.list_filtered(offset=offset, limit=size, **kwargs)
        return {"items": items, "total": total, "page": page, "size": size}

    def get_event(self, event_id: int):
        event = self.event_repo.get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")
        return event

    def update_event(self, event_id: int, data: schemas.EventCreate):
        event = self.get_event(event_id)
        
        # Look up activity type to validate max participants if changed
        if data.activity_type_id != event.activity_type_id or data.target_participants != event.target_participants:
             activity_type = self.activity_repo.get(data.activity_type_id)
             if activity_type and data.target_participants > activity_type.max_participants:
                  # Just warning or block? Frontend blocks, backend should too ideally, but let's trust frontend or generic validation
                  pass
        
        updated_event = self.event_repo.update(event, data.dict())
        return updated_event

    def delete_event(self, event_id: int):
        event = self.get_event(event_id)
        # SQLAlchemy cascade="all, delete-orphan" on relationship should handle attendees
        self.event_repo.delete(event)
        return {"message": "Kegiatan berhasil dihapus"}


    def add_attendee(self, data: schemas.AttendeeCreate, force_add: bool = False):
        # Check if user already attended this event (Unique constraint handle or check)
        existing = self.attendee_repo.get_by_event_and_nik(data.event_id, data.nik)
        if existing:
            raise HTTPException(status_code=400, detail="NIK already registered for this event")
        
        # If not force_add, check for duplicates across other events
        if not force_add:
            duplicates = self.check_nik_duplicates(data.nik, data.event_id)
            if duplicates["exists"]:
                raise HTTPException(
                    status_code=409,  # Conflict status
                    detail={
                        "type": "duplicate_warning",
                        "message": "NIK sudah terdaftar di kegiatan lain",
                        "activities": duplicates["activities"]
                    }
                )
        
        # Check capacity
        event = self.event_repo.db.query(models.Event).get(data.event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        current_count = self.attendee_repo.count_by_event(data.event_id)
        if event.activity_type and current_count >= event.activity_type.max_participants:
             raise HTTPException(status_code=400, detail="Event capacity reached")

        obj = models.Attendee(**data.dict())
        return self.attendee_repo.create(obj)

    def check_nik_duplicates(self, nik: str, current_event_id: int = None):
        """Check if NIK exists in other events, return activity info"""
        existing = self.attendee_repo.get_all_by_nik(nik)
        
        # Filter out current event if provided
        if current_event_id:
            existing = [a for a in existing if a.event_id != current_event_id]
        
        if not existing:
            return {"exists": False, "activities": []}
        
        # Get activity details for each duplicate
        activities = []
        for attendee in existing:
            event = self.event_repo.db.query(models.Event).get(attendee.event_id)
            if event:
                location_parts = []
                if event.kecamatan:
                    location_parts.append(event.kecamatan)
                if event.desa:
                    location_parts.append(event.desa)
                location = ", ".join(location_parts) if location_parts else (event.dapil or "-")
                
                activities.append({
                    "activity_name": event.activity_type.name if event.activity_type else "Unknown",
                    "date": str(event.date),
                    "location": location
                })
        
        return {"exists": True, "activities": activities}

    def list_attendees(self, event_id: int, page=1, size=50):
        offset = (page - 1) * size
        items = self.attendee_repo.list_by_event(event_id, offset, size)
        # return items (total could be added)
        return items

    def get_recent_events(self, limit=5):
        events = self.event_repo.db.query(models.Event).order_by(models.Event.date.desc()).limit(limit).all()
        
        results = []
        for e in events:
            # Participants count
            count = self.attendee_repo.count_by_event(e.id)
            
            # Location string logic
            location = f"Dapil {e.dapil}"
            if e.location_hierarchy and isinstance(e.location_hierarchy, dict):
                 if e.location_hierarchy.get("kecamatan"):
                     location = e.location_hierarchy.get("kecamatan")
            
            results.append({
                "id": e.id,
                "location": location,
                "date": e.date,
                "type": e.activity_type.name if e.activity_type else "General",
                "participants": count
            })
        return results

    def list_all_attendees(self, kecamatan: list[str] = None, desa: str = None):
        """Get all attendees with optional location filters for export"""
        query = self.attendee_repo.db.query(models.Attendee)
        
        if kecamatan:
            if isinstance(kecamatan, list):
                query = query.filter(models.Attendee.kecamatan.in_(kecamatan))
            else:
                query = query.filter(models.Attendee.kecamatan == kecamatan)
        if desa:
            query = query.filter(models.Attendee.desa == desa)
            
        attendees = query.all()
        return [
            {
                "id": a.id,
                "nik": a.nik,
                "name": a.name,
                "kecamatan": a.kecamatan,
                "desa": a.desa,
                "alamat": getattr(a, 'alamat', None),  # New SABADESA field
                "jenis_kelamin": getattr(a, 'jenis_kelamin', None),
                "pekerjaan": getattr(a, 'pekerjaan', None),
                "usia": getattr(a, 'usia', None),
            }
            for a in attendees
        ]
