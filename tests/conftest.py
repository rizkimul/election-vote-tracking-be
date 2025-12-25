import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app
from app.deps import get_db, get_auth_service, get_current_user
from app.models import User
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a new TestClient that uses the test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    # We clear other overrides to ensure auth service uses the test DB
    app.dependency_overrides[get_auth_service] = lambda: AuthService(UserRepository(db_session))
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from app.services.auth_service import AuthService
    from app.repositories.user_repo import UserRepository
    
    repo = UserRepository(db_session)
    auth = AuthService(repo)
    user = auth.register("testuser", "Test User", "password123", "1234567890123456")
    db_session.commit()
    db_session.refresh(user)
    return user
