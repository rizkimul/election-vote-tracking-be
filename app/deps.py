from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from .database import get_db
from .repositories.user_repo import UserRepository
from .repositories.vote_repo import VoteRepository
from .repositories.engagement_repo import EngagementRepository
from .services.auth_service import AuthService
from .services.vote_service import VoteService
from .services.engagement_service import EngagementService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Repositories
def get_user_repo(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_vote_repo(db: Session = Depends(get_db)):
    return VoteRepository(db)

def get_engagement_repo(db: Session = Depends(get_db)):
    return EngagementRepository(db)

# Services
def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)):
    return AuthService(user_repo)

def get_vote_service(vote_repo: VoteRepository = Depends(get_vote_repo)):
    return VoteService(vote_repo)

def get_engagement_service(eng_repo: EngagementRepository = Depends(get_engagement_repo)):
    return EngagementService(eng_repo)

# --- Authenticated user dependency ---
def get_current_user(token: str = Depends(oauth2_scheme),
                     auth_svc: AuthService = Depends(get_auth_service),
                     user_repo: UserRepository = Depends(get_user_repo)):
    payload = auth_svc.decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    nik = payload["sub"]
    user = user_repo.get_by_nik(nik)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
