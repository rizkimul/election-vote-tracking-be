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

@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers from logged in test user."""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def activity_type(db_session):
    """Create a test activity type."""
    from app.models import ActivityType
    at = ActivityType(name="Test Activity", max_participants=50)
    db_session.add(at)
    db_session.commit()
    db_session.refresh(at)
    return at

@pytest.fixture
def event(db_session, activity_type):
    """Create a test event."""
    from app.models import Event
    from datetime import date
    e = Event(
        activity_type_id=activity_type.id,
        kecamatan="Dayeuhkolot",
        desa="Cangkuang Kulon",
        dapil="1",
        date=date(2024, 12, 1),
        target_participants=30
    )
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)
    return e

@pytest.fixture
def attendee(db_session, event):
    """Create a test attendee."""
    from app.models import Attendee
    a = Attendee(
        event_id=event.id,
        nik="1234567890123456",
        identifier_type="NIK",
        name="Test Attendee",
        kecamatan="Dayeuhkolot",
        desa="Cangkuang Kulon",
        alamat="Jl. Test No. 1",
        jenis_kelamin="L",
        pekerjaan="Wiraswasta",
        usia=30
    )
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)
    return a

@pytest.fixture
def historical_vote(db_session):
    """Create a test historical vote."""
    from app.models import HistoricalVote
    hv = HistoricalVote(
        dapil="Dapil 1",
        kabupaten="Kabupaten Bandung",
        kecamatan="Dayeuhkolot",
        desa="Cangkuang Kulon",
        election_year=2024,
        data={"PDIP": 100, "Golkar": 50},
        total_votes=150
    )
    db_session.add(hv)
    db_session.commit()
    db_session.refresh(hv)
    return hv
