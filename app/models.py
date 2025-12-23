from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nik = Column(String, unique=True, index=True, nullable=True)  # Keep for backward compatibility
    username = Column(String, unique=True, index=True, nullable=True)  # New login field
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")


class HistoricalVote(Base):
    __tablename__ = "historical_votes"
    id = Column(Integer, primary_key=True, index=True)
    dapil = Column(String, index=True)
    kabupaten = Column(String, index=True)
    kecamatan = Column(String, index=True)
    desa = Column(String, index=True)
    data = Column(JSON)  # Stores { "Partai A": 100, "Partai B": 50 } or similar breakdown
    total_votes = Column(Integer)
    election_year = Column(Integer, index=True)
    source = Column(String, default="import", index=True) # "import" or "manual"


class ActivityType(Base):
    __tablename__ = "activity_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    max_participants = Column(Integer, default=100)
    
    events = relationship("Event", back_populates="activity_type", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"))
    dapil = Column(String, nullable=True)  # Category above kecamatan (kept for hierarchy)
    kecamatan = Column(String, nullable=False)  # New: Primary location field
    desa = Column(String, nullable=True)  # New: Desa/Kelurahan
    # location_hierarchy can store JSON like {"kabupaten": "X", "kecamatan": "Y"}
    location_hierarchy = Column(JSON, nullable=True) 
    date = Column(Date, nullable=False)
    target_participants = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    activity_type = relationship("ActivityType", back_populates="events")
    attendees = relationship("Attendee", back_populates="event", cascade="all, delete-orphan")


class Attendee(Base):
    __tablename__ = "attendees"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    
    # Identifier fields - NIK or NIS (for education activities)
    nik = Column(String, index=True, nullable=False)  # Stores NIK or NIS value
    identifier_type = Column(String, default="NIK")  # "NIK" or "NIS"
    name = Column(String)
    
    # Location fields
    kecamatan = Column(String, nullable=True)
    desa = Column(String, nullable=True)
    alamat = Column(String, nullable=True)  # Combined address (replaces kampung + RT/RW)
    
    # New demographic fields for SABADESA
    jenis_kelamin = Column(String, nullable=True)  # "L" (Laki-laki) or "P" (Perempuan)
    pekerjaan = Column(String, nullable=True)  # Occupation
    usia = Column(Integer, nullable=True)  # Age in years
    
    # Legacy fields (kept for backward compatibility)
    kampung = Column(String, nullable=True)
    rt_rw = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    event = relationship("Event", back_populates="attendees")

    # Unique constraint: Same NIK/NIS cannot be added to the same event twice
    # But same NIK CAN attend multiple different events
    __table_args__ = (UniqueConstraint('event_id', 'nik', name='unique_attendee_per_event'),)


class ImportLog(Base):
    __tablename__ = "import_logs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False) # "success", "failed", "partial"
    records_count = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


