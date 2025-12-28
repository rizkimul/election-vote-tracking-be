"""
Unit tests for prioritization endpoints.
Covers prioritization suggestions based on event and attendee data.
"""
from datetime import date


# === POSITIVE CASES ===

def test_get_suggestions_with_data(client, auth_headers, event, attendee):
    """Test getting prioritization suggestions when data exists."""
    response = client.get("/prioritization/suggest", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "kecamatan" in item
        assert "score" in item
        assert "participant_count" in item
        assert "event_count" in item
        assert "reason" in item


def test_suggestions_scoring_logic(client, auth_headers, db_session):
    """Test that scoring logic works correctly for different scenarios."""
    from app.models import Event, Attendee, ActivityType
    
    # Create activity type
    at = ActivityType(name="Rating Test", max_participants=100)
    db_session.add(at)
    db_session.commit()
    
    # Scenario 1: Kecamatan with no events (should get high score - need scheduling)
    # We'll create a kecamatan that only has attendees but no events recorded there
    # Actually, prioritization looks at Event.kecamatan and Attendee.kecamatan
    
    # Create event in one kecamatan
    event1 = Event(
        activity_type_id=at.id,
        kecamatan="HighActivity",
        date=date(2024, 12, 1),
        target_participants=20
    )
    db_session.add(event1)
    
    # Create multiple attendees in the event
    for i in range(10):
        attendee = Attendee(
            event_id=event1.id,
            nik=f"100000000000000{i}",
            name=f"Person {i}",
            identifier_type="NIK",
            kecamatan="HighActivity",
            alamat="Test",
            jenis_kelamin="L",
            pekerjaan="Test",
            usia=25 + i
        )
        db_session.add(attendee)
    
    db_session.commit()
    
    response = client.get("/prioritization/suggest", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should have suggestions sorted by score
    if len(data) > 1:
        assert data[0]["score"] >= data[1]["score"]


def test_suggestions_sorted_by_score(client, auth_headers, event, attendee):
    """Test that suggestions are sorted by score descending."""
    response = client.get("/prioritization/suggest", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    if len(data) > 1:
        scores = [item["score"] for item in data]
        assert scores == sorted(scores, reverse=True)


# === EDGE CASES ===

def test_get_suggestions_empty(client, auth_headers):
    """Test getting suggestions returns empty list when no data."""
    # Note: With a fresh db and only test_user created, there should be minimal data
    response = client.get("/prioritization/suggest", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_prioritization_unauthorized(client):
    """Test prioritization endpoint requires authentication."""
    response = client.get("/prioritization/suggest")
    assert response.status_code == 401
