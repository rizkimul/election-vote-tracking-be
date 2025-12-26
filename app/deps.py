from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from .database import get_db
from .repositories.user_repo import UserRepository
from .repositories.historical_vote_repo import HistoricalVoteRepository
from .repositories.event_repo import EventRepository
from .repositories.attendee_repo import AttendeeRepository
from .repositories.activity_type_repo import ActivityTypeRepository

from .services.auth_service import AuthService
from .services.historical_vote_service import HistoricalVoteService
from .services.event_service import EventService
from .services.activity_type_service import ActivityTypeService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Repositories
def get_user_repo(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_historical_vote_repo(db: Session = Depends(get_db)):
    return HistoricalVoteRepository(db)

def get_event_repo(db: Session = Depends(get_db)):
    return EventRepository(db)

def get_attendee_repo(db: Session = Depends(get_db)):
    return AttendeeRepository(db)

def get_activity_type_repo(db: Session = Depends(get_db)):
    return ActivityTypeRepository(db)

# Services
def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)):
    return AuthService(user_repo)

def get_historical_vote_service(repo: HistoricalVoteRepository = Depends(get_historical_vote_repo)):
    return HistoricalVoteService(repo)

def get_event_service(
    event_repo: EventRepository = Depends(get_event_repo),
    attendee_repo: AttendeeRepository = Depends(get_attendee_repo),
    activity_repo: ActivityTypeRepository = Depends(get_activity_type_repo)
):
    return EventService(event_repo, attendee_repo, activity_repo)

def get_activity_type_service(repo: ActivityTypeRepository = Depends(get_activity_type_repo)):
    return ActivityTypeService(repo)

from .services.analytics_service import AnalyticsService
def get_analytics_service(
    event_repo: EventRepository = Depends(get_event_repo),
    attendee_repo: AttendeeRepository = Depends(get_attendee_repo),
    activity_repo: ActivityTypeRepository = Depends(get_activity_type_repo)
):
    return AnalyticsService(event_repo, attendee_repo, activity_repo)

from .services.prioritization_service import PrioritizationService
def get_prioritization_service(
    event_repo: EventRepository = Depends(get_event_repo),
    attendee_repo: AttendeeRepository = Depends(get_attendee_repo)
):
    return PrioritizationService(event_repo, attendee_repo)

# --- Authenticated user dependency ---
def get_current_user(token: str = Depends(oauth2_scheme),
                     auth_svc: AuthService = Depends(get_auth_service),
                     user_repo: UserRepository = Depends(get_user_repo)):
    payload = auth_svc.decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kredensial otentikasi tidak valid")
    identifier = payload["sub"]
    # Try username first (SABADESA), then fallback to NIK (legacy)
    user = user_repo.get_by_username(identifier)
    if not user:
        user = user_repo.get_by_nik(identifier)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Pengguna tidak ditemukan")
    return user

