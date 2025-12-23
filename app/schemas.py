from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional, Generic, List, TypeVar
from datetime import date, datetime
import re

# ... (imports)
T = TypeVar('T')

def validate_nik(v: str) -> str:
    """Validate NIK (16 digits) - only for traditional NIK"""
    if not re.match(r'^\d{16}$', v):
        raise ValueError('NIK must be 16 digits')
    return v

def validate_nik_or_nis(v: str, identifier_type: str = "NIK") -> str:
    """Flexible validation for NIK or NIS (education ID)"""
    if identifier_type == "NIK":
        if not re.match(r'^\d{16}$', v):
            raise ValueError('NIK must be 16 digits')
    else:  # NIS
        if not re.match(r'^\d{1,20}$', v):
            raise ValueError('NIS must be numeric (1-20 digits)')
    return v

# --- Auth ---
class UserCreate(BaseModel):
    username: str  # New: username-based auth for SABADESA
    name: str
    password: str
    nik: Optional[str] = None  # Optional for backward compatibility

    @field_validator('nik')
    def nik_must_be_valid(cls, v):
        if v is not None:
            return validate_nik(v)
        return v

class UserOut(BaseModel):
    id: int
    username: Optional[str] = None
    nik: Optional[str] = None
    name: str
    class Config:
        orm_mode = True

class LoginSchema(BaseModel):
    username: str  # Changed from NIK to username
    password: str

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
    kecamatan: str  # Primary location field
    desa: Optional[str] = None  # Desa/Kelurahan
    dapil: Optional[str] = None  # Category above kecamatan (optional)
    location_hierarchy: Optional[Dict[str, Any]] = None
    date: date
    target_participants: int

class EventOut(BaseModel):
    id: int
    activity_type_id: int
    kecamatan: Optional[str] = None  # Made optional for legacy/missing data compatibility
    desa: Optional[str] = None
    dapil: Optional[str] = None
    location_hierarchy: Optional[Dict[str, Any]] = None
    date: date
    target_participants: int
    created_at: datetime
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
    nik: str  # Stores NIK or NIS value
    identifier_type: str = "NIK"  # "NIK" or "NIS"
    name: str
    kecamatan: Optional[str] = None
    desa: Optional[str] = None
    alamat: Optional[str] = None  # Combined address
    jenis_kelamin: Optional[str] = None  # "L" or "P"
    pekerjaan: Optional[str] = None  # Occupation
    usia: Optional[int] = None  # Age in years
    # Legacy fields (kept for backward compatibility)
    kampung: Optional[str] = None
    rt_rw: Optional[str] = None

class AttendeeOut(BaseModel):
    id: int
    event_id: int
    nik: str
    identifier_type: str
    name: Optional[str] = None
    kecamatan: Optional[str] = None
    desa: Optional[str] = None
    alamat: Optional[str] = None
    jenis_kelamin: Optional[str] = None
    pekerjaan: Optional[str] = None
    usia: Optional[int] = None
    created_at: datetime
    class Config:
        orm_mode = True

class ResponseData(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: T