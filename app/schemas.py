from pydantic import BaseModel
from datetime import date
from typing import Optional, TypeVar, Generic

T = TypeVar('T')

# --- Auth ---
class UserCreate(BaseModel):
    nik: str
    name: str
    password: str

class UserOut(BaseModel):
    id: int
    nik: str
    name: str
    class Config:
        orm_mode = True

class LoginSchema(BaseModel):
    nik: str
    password: str

# --- Vote ---
class VoteCreate(BaseModel):
    district: str
    sub_district: str
    village: str
    total_votes: int
    election_year: int

class VoteOut(VoteCreate):
    id: int
    class Config:
        orm_mode = True

# --- Engagement ---
class EngagementCreate(BaseModel):
    nik: str
    name: str
    district: str
    sub_district: str
    village: str
    hamlet: str
    rt_rw: str
    event_type: str
    participants: int
    date: date
    lat: Optional[float] = None
    lng: Optional[float] = None

class EngagementOut(EngagementCreate):
    id: int
    class Config:
        orm_mode = True

class ResponseData(BaseModel, Generic[T]):
    status_code: int
    message: str
    data: T