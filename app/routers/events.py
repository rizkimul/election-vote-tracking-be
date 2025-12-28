from fastapi import APIRouter, Depends, Query, HTTPException
from ..schemas import EventCreate, EventOut, AttendeeCreate, AttendeeOut, EventListResponse
from ..deps import get_event_service, get_current_user
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventOut)
def create_event(payload: EventCreate, svc = Depends(get_event_service), user = Depends(get_current_user)):
    try:
        return svc.create_event(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
def get_recent_events(limit: int = 5, svc = Depends(get_event_service), user = Depends(get_current_user)):
    return svc.get_recent_events(limit=limit)

@router.get("/", response_model=EventListResponse)
def list_events(page: int = Query(1, ge=1),
                size: int = Query(20, ge=1, le=200),
                dapil: Optional[str] = None,
                date_from: Optional[date] = None,
                date_to: Optional[date] = None,
                activity_type_id: Optional[int] = None,
                search: Optional[str] = Query(None, description="Search by activity name or kecamatan"),
                svc = Depends(get_event_service),
                user = Depends(get_current_user)):
    # Returning dict with items/total/page/size
    return svc.list_events(page=page, size=size, dapil=dapil, date_from=date_from, date_to=date_to, activity_type_id=activity_type_id, search=search)

@router.get("/check-nik/{nik}")
def check_nik_duplicate(
    nik: str, 
    current_event_id: Optional[int] = None,
    svc = Depends(get_event_service), 
    user = Depends(get_current_user)
):
    """Check if NIK exists in any events, return activity info"""
    return svc.check_nik_duplicates(nik, current_event_id)

@router.post("/attendees", response_model=AttendeeOut)
def add_attendee(
    payload: AttendeeCreate, 
    force_add: bool = Query(False, description="Force add even if NIK exists in other events"),
    svc = Depends(get_event_service), 
    user = Depends(get_current_user)
):
    return svc.add_attendee(payload, force_add=force_add)

@router.get("/attendees/all")
def list_all_attendees(
    kecamatan: Optional[List[str]] = Query(None),
    desa: Optional[str] = None,
    svc = Depends(get_event_service), 
    user = Depends(get_current_user)
):
    """Get all attendees with optional filters for export functionality"""
    return svc.list_all_attendees(kecamatan=kecamatan, desa=desa)

@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, payload: EventCreate, svc = Depends(get_event_service), user = Depends(get_current_user)):
    try:
        return svc.update_event(event_id, payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{event_id}")
def delete_event(event_id: int, svc = Depends(get_event_service), user = Depends(get_current_user)):
    try:
        return svc.delete_event(event_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{event_id}/attendees", response_model=List[AttendeeOut])
def list_attendees(event_id: int, 
                   page: int = 1, 
                   size: int = 50, 
                   svc = Depends(get_event_service), 
                   user = Depends(get_current_user)):
    return svc.list_attendees(event_id, page, size)
