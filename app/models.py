from sqlalchemy import Column, Integer, String, Date, Float
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nik = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")


class VoteResult(Base):
    __tablename__ = "vote_results"
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String, index=True)
    sub_district = Column(String, index=True)
    village = Column(String, index=True)
    total_votes = Column(Integer)
    election_year = Column(Integer, index=True)


class Engagement(Base):
    __tablename__ = "engagements"
    id = Column(Integer, primary_key=True, index=True)
    nik = Column(String, index=True)
    name = Column(String)
    district = Column(String)
    sub_district = Column(String)
    village = Column(String)
    hamlet = Column(String)
    rt_rw = Column(String)
    event_type = Column(String)  # recess, oversight, education, dialogue, cultural
    participants = Column(Integer)
    date = Column(Date)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
