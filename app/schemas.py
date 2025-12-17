from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional, Generic, List, TypeVar
from datetime import date, datetime
import re

# ... (imports)
T = TypeVar('T')

def validate_nik(v: str) -> str:
    if not re.match(r'^\d{16}$', v):
        raise ValueError('NIK must be 16 digits')
    return v

# --- Auth ---
class UserCreate(BaseModel):
    nik: str
    name: str
    password: str

    @field_validator('nik')
    def nik_must_be_valid(cls, v):
        return validate_nik(v)

class UserOut(BaseModel):
    id: int
    nik: str
    name: str
    class Config:
        orm_mode = True

class LoginSchema(BaseModel):
    nik: str
    password: str
    
    @field_validator('nik')
    def nik_must_be_valid(cls, v):
        return validate_nik(v)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# --- Historical Vote ---
class HistoricalVoteCreate(BaseModel):
    dapil: str
    kabupaten: str
    kecamatan: str
    desa: str
    data: Dict[str, int] # e.g. {"PDIP": 100, "Golkar": 50}
    total_votes: int
    election_year: int

class HistoricalVoteOut(HistoricalVoteCreate):
    id: int
    class Config:
        orm_mode = True

# --- Activity Type ---
class ActivityTypeCreate(BaseModel):
    name: str
    max_participants: int

class ActivityTypeOut(ActivityTypeCreate):
    id: int
    class Config:
        orm_mode = True

# --- Event ---
class EventCreate(BaseModel):
    activity_type_id: int
    dapil: str
    location_hierarchy: Optional[Dict[str, Any]] = None
    date: date
    target_participants: int

class EventOut(EventCreate):
    id: int
    created_at: datetime
    # Could nest activity_type info here if needed
    class Config:
        orm_mode = True

class EventListResponse(BaseModel):
    items: List[EventOut]
    total: int
    page: int
    size: int

# --- Attendee ---
class AttendeeCreate(BaseModel):
    event_id: int
    nik: str
    name: str
    kecamatan: Optional[str] = None
    desa: Optional[str] = None
    kampung: Optional[str] = None
    rt_rw: Optional[str] = None

    @field_validator('nik')
    def nik_must_be_valid(cls, v):
        return validate_nik(v)

class AttendeeOut(AttendeeCreate):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class ResponseData(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: T