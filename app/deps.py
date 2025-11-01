from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .repositories.user_repo import UserRepository
from .repositories.vote_repo import VoteRepository
from .repositories.engagement_repo import EngagementRepository
from .services.auth_service import AuthService
from .services.vote_service import VoteService
from .services.engagement_service import EngagementService

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
