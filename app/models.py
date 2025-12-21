from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nik = Column(String, unique=True, index=True, nullable=False)
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
    dapil = Column(String, nullable=False)
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
    nik = Column(String, index=True, nullable=False) # Unique index per requirements (one person, one vote/attendance context?)
    name = Column(String)
    
    # Redundant location data for easier flat querying/heatmap if needed, 
    # or rely on Event. For now, keeping flat location details from PRD might be useful 
    # but PRD says "Link attendees to specific events".
    # I will keep NIK and Name as primary. 
    # If the user wants granular "Hamlet/RT/RW" per attendee (which is deeper than Event location), add it.
    # PRD "Manual Potensi Suara Entry" -> NIK, Nama, Kecamatan, Desa, Kampung, RT/RW.
    kecamatan = Column(String, nullable=True)
    desa = Column(String, nullable=True)
    kampung = Column(String, nullable=True)
    rt_rw = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    event = relationship("Event", back_populates="attendees")

    # PRD: "Prevent duplicate NIK entries". 
    # Implementing Unique Constraint on NIK. 
    # If this should be Per Event, we change to (event_id, nik).
    # Based on approved plan assumption:
    __table_args__ = (UniqueConstraint('nik', name='unique_attendee_nik'),)


class ImportLog(Base):
    __tablename__ = "import_logs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False) # "success", "failed", "partial"
    records_count = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


