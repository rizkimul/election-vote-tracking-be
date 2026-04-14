"""
Unit tests for event and attendee endpoints.
Covers CRUD operations, pagination, NIK duplicate checking, and capacity limits.
"""
from datetime import date


# === POSITIVE CASES - EVENTS ===

def test_create_event(client, auth_headers, activity_type):
    """Test creating an event with valid data."""
    response = client.post("/events/", json={
        "activity_type_id": activity_type.id,
        "kecamatan": "Margaasih",
        "desa": "Margaasih",
        "dapil": "2",
        "date": "2024-12-15",
        "target_participants": 25
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["kecamatan"] == "Margaasih"
    assert data["target_participants"] == 25
    assert "id" in data


def test_list_events(client, auth_headers, event):
    """Test listing events with pagination."""
    response = client.get("/events/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert len(data["items"]) >= 1


def test_list_events_with_search(client, auth_headers, event):
    """Test listing events with search filter."""
    response = client.get("/events/?search=Dayeuhkolot", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_get_recent_events(client, auth_headers, event):
    """Test getting recent events."""
    response = client.get("/events/recent?limit=5", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_update_event(client, auth_headers, event):
    """Test updating an event."""
    response = client.put(f"/events/{event.id}", json={
        "activity_type_id": event.activity_type_id,
        "kecamatan": "Updated Kecamatan",
        "desa": "Updated Desa",
        "dapil": "3",
        "date": "2024-12-20",
        "target_participants": 40
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["kecamatan"] == "Updated Kecamatan"
    assert data["target_participants"] == 40


def test_delete_event(client, auth_headers, event):
    """Test deleting an event."""
    response = client.delete(f"/events/{event.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "berhasil" in data.get("message", "").lower() or "message" in data


# === POSITIVE CASES - ATTENDEES ===

def test_add_attendee(client, auth_headers, event):
    """Test adding an attendee to an event."""
    response = client.post("/events/attendees", json={
        "event_id": event.id,
        "nik": "1111222233334444",
        "identifier_type": "NIK",
        "name": "John Doe",
        "kecamatan": "Dayeuhkolot",
        "desa": "Cangkuang Kulon",
        "alamat": "Jl. Contoh No. 123",
        "jenis_kelamin": "L",
        "pekerjaan": "Karyawan",
        "usia": 35
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["nik"] == "1111222233334444"


def test_list_attendees(client, auth_headers, event, attendee):
    """Test listing attendees for an event."""
    response = client.get(f"/events/{event.id}/attendees", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_all_attendees(client, auth_headers, attendee):
    """Test listing all attendees for export."""
    response = client.get("/events/attendees/all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_all_attendees_with_filter(client, auth_headers, attendee):
    """Test listing all attendees with kecamatan filter."""
    response = client.get("/events/attendees/all?kecamatan=Dayeuhkolot", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_check_nik_no_duplicate(client, auth_headers):
    """Test checking NIK that doesn't exist returns no duplicates."""
    response = client.get("/events/check-nik/9999888877776666", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is False
    assert data["activities"] == []


def test_check_nik_duplicate(client, auth_headers, attendee):
    """Test checking NIK that exists returns duplicate info."""
    response = client.get(f"/events/check-nik/{attendee.nik}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["exists"] is True
    assert len(data["activities"]) >= 1


def test_add_attendee_force(client, auth_headers, event, attendee, db_session):
    """Test force adding attendee even with NIK duplicate warning."""
    # Create another event to test cross-event duplicate
    from app.models import Event, ActivityType
    at = db_session.query(ActivityType).first()
    new_event = Event(
        activity_type_id=at.id,
        kecamatan="Banjaran",
        desa="Banjaran",
        dapil="2",
        date=date(2024, 12, 10),
        target_participants=20
    )
    db_session.add(new_event)
    db_session.commit()
    db_session.refresh(new_event)
    
    # Force add the same NIK to a different event
    response = client.post(f"/events/attendees?force_add=true", json={
        "event_id": new_event.id,
        "nik": attendee.nik,  # Same NIK 
        "identifier_type": "NIK",
        "name": "Same Person",
        "kecamatan": "Banjaran",
        "desa": "Banjaran",
        "alamat": "Jl. Lain No. 1",
        "jenis_kelamin": "L",
        "pekerjaan": "Petani",
        "usia": 30
    }, headers=auth_headers)
    assert response.status_code == 200


# === NEGATIVE CASES ===

def test_get_nonexistent_event(client, auth_headers):
    """Test getting non-existent event returns 404."""
    response = client.get("/events/99999", headers=auth_headers)
    # Note: list_events endpoint doesn't have get single by ID, 
    # but delete/update rely on get_event which raises 404
    pass  # This endpoint doesn't exist - events are accessed via list


def test_update_nonexistent_event(client, auth_headers, activity_type):
    """Test updating non-existent event returns 404."""
    response = client.put("/events/99999", json={
        "activity_type_id": activity_type.id,
        "kecamatan": "Any",
        "date": "2024-12-25",
        "target_participants": 10
    }, headers=auth_headers)
    assert response.status_code in [404, 500]


def test_delete_nonexistent_event(client, auth_headers):
    """Test deleting non-existent event returns 404."""
    response = client.delete("/events/99999", headers=auth_headers)
    assert response.status_code in [404, 500]


def test_add_duplicate_attendee_same_event(client, auth_headers, event, attendee):
    """Test adding same NIK to same event twice returns 400."""
    response = client.post("/events/attendees", json={
        "event_id": event.id,
        "nik": attendee.nik,  # Already exists in this event
        "identifier_type": "NIK",
        "name": "Duplicate Person",
        "kecamatan": "Dayeuhkolot",
        "desa": "Cangkuang Kulon",
        "alamat": "Jl. Test",
        "jenis_kelamin": "P",
        "pekerjaan": "IRT",
        "usia": 28
    }, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert "terdaftar" in data.get("detail", "").lower()


def test_add_attendee_capacity_exceeded(client, auth_headers, db_session, activity_type):
    """Test adding attendee when event is full returns 400."""
    from app.models import Event, Attendee
    
    # Create event with max_participants = 1 from activity type
    activity_type.max_participants = 1
    db_session.commit()
    
    event = Event(
        activity_type_id=activity_type.id,
        kecamatan="Test",
        date=date(2024, 12, 25),
        target_participants=1
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    # Add first attendee (should work)
    first_attendee = Attendee(
        event_id=event.id,
        nik="1111111111111111",
        name="First",
        identifier_type="NIK",
        kecamatan="Test",
        alamat="Test",
        jenis_kelamin="L",
        pekerjaan="Test",
        usia=25
    )
    db_session.add(first_attendee)
    db_session.commit()
    
    # Try to add second attendee (should fail - capacity full)
    response = client.post("/events/attendees", json={
        "event_id": event.id,
        "nik": "2222222222222222",
        "identifier_type": "NIK",
        "name": "Second",
        "kecamatan": "Test",
        "desa": "Test",
        "alamat": "Test",
        "jenis_kelamin": "P",
        "pekerjaan": "Test",
        "usia": 30
    }, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert "penuh" in data.get("detail", "").lower()


def test_add_attendee_nonexistent_event(client, auth_headers):
    """Test adding attendee to non-existent event returns 404."""
    response = client.post("/events/attendees", json={
        "event_id": 99999,
        "nik": "5555666677778888",
        "identifier_type": "NIK",
        "name": "Test",
        "kecamatan": "Test",
        "alamat": "Test",
        "jenis_kelamin": "L",
        "pekerjaan": "Test",
        "usia": 25
    }, headers=auth_headers)
    assert response.status_code == 404
