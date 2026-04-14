"""
Unit tests for analytics endpoints.
Covers global stats, heatmap data, engagement trends, and distribution metrics.
"""


# === POSITIVE CASES ===

def test_get_global_stats(client, auth_headers, event, attendee):
    """Test getting global stats."""
    response = client.get("/analytics/global", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "total_attendees" in data
    assert "wilayah_count" in data
    assert "desa_count" in data


def test_get_global_stats_with_kecamatan(client, auth_headers, attendee):
    """Test getting global stats filtered by kecamatan."""
    response = client.get("/analytics/global?kecamatan=Dayeuhkolot", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_attendees" in data


def test_get_votes_summary(client, auth_headers):
    """Test getting votes summary (returns empty list in SABADESA)."""
    response = client.get("/analytics/votes/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_heatmap_data(client, auth_headers, attendee):
    """Test getting heatmap data at kecamatan level."""
    response = client.get("/analytics/heatmap?level=kecamatan", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "kecamatan" in data[0]
        assert "intensity" in data[0]


def test_get_heatmap_data_desa_level(client, auth_headers, attendee):
    """Test getting heatmap data at desa level."""
    response = client.get("/analytics/heatmap?level=desa", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_heatmap_data_all_levels(client, auth_headers, attendee):
    """Test getting heatmap data at all levels."""
    response = client.get("/analytics/heatmap?level=all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_engagement_trends(client, auth_headers, event, attendee):
    """Test getting engagement trends."""
    response = client.get("/analytics/engagement/trends", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "month" in data[0]
        assert "participants" in data[0]


def test_get_activity_distribution(client, auth_headers, event):
    """Test getting activity distribution."""
    response = client.get("/analytics/activities/distribution", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "name" in data[0]
        assert "value" in data[0]


def test_get_gender_distribution(client, auth_headers, attendee):
    """Test getting gender distribution."""
    response = client.get("/analytics/participants/gender", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "name" in data[0]
        assert "value" in data[0]


def test_get_age_distribution(client, auth_headers, attendee):
    """Test getting age distribution."""
    response = client.get("/analytics/participants/age", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "name" in data[0]
        assert "value" in data[0]


def test_get_activities_per_kecamatan(client, auth_headers, event):
    """Test getting activities per kecamatan."""
    response = client.get("/analytics/activities/per-kecamatan", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "name" in data[0]
        assert "value" in data[0]


# === EDGE CASES ===

def test_analytics_empty_data(client, auth_headers):
    """Test analytics endpoints return valid response with empty data."""
    # Note: This test uses a fresh db without seeded data
    # The fixtures haven't been called, so db should have minimal data
    
    response = client.get("/analytics/global", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] >= 0
    assert data["total_attendees"] >= 0


def test_analytics_unauthorized(client):
    """Test analytics endpoints require authentication."""
    response = client.get("/analytics/global")
    assert response.status_code == 401
