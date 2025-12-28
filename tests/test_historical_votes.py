"""
Unit tests for historical votes endpoints.
NOTE: The historical_votes router is currently DISABLED in main.py (SABADESA doesn't use vote tracking).
These tests are kept for reference and will pass once the router is re-enabled.
"""
import pytest


# Skip all tests in this module since the router is disabled
pytestmark = pytest.mark.skip(reason="historical_votes router is disabled in main.py (SABADESA)")


# === POSITIVE CASES ===

def test_add_historical_vote(client, auth_headers):
    """Test adding a historical vote record."""
    response = client.post("/historical-votes/", json={
        "dapil": "Dapil 2",
        "kabupaten": "Kabupaten Bandung",
        "kecamatan": "Margaasih",
        "desa": "Margaasih",
        "election_year": 2024,
        "data": {"PDIP": 200, "Golkar": 150, "PKB": 100},
        "total_votes": 450
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["dapil"] == "Dapil 2"
    assert data["kecamatan"] == "Margaasih"
    assert data["total_votes"] == 450
    assert "id" in data


def test_list_historical_votes(client, auth_headers, historical_vote):
    """Test listing historical votes with pagination."""
    response = client.get("/historical-votes/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_votes_with_pagination(client, auth_headers, historical_vote):
    """Test listing votes with page and size parameters."""
    response = client.get("/historical-votes/?page=1&size=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_votes_with_filters(client, auth_headers, historical_vote):
    """Test listing votes with various filters."""
    response = client.get(
        "/historical-votes/?dapil=Dapil%201&kecamatan=Dayeuhkolot&election_year=2024", 
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_filter_options(client, auth_headers, historical_vote):
    """Test getting filter options."""
    response = client.get("/historical-votes/filters", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "dapils" in data
    assert "kecamatans" in data
    assert isinstance(data["dapils"], list)
    assert isinstance(data["kecamatans"], list)


def test_get_filter_options_with_dapil(client, auth_headers, historical_vote):
    """Test getting filter options filtered by dapil."""
    response = client.get("/historical-votes/filters?dapil=Dapil%201", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "kecamatans" in data


def test_get_import_logs(client, auth_headers):
    """Test getting import logs."""
    response = client.get("/historical-votes/import-history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# === EDGE CASES ===

def test_list_votes_empty(client, auth_headers):
    """Test listing votes returns empty list when no data matches filter."""
    response = client.get(
        "/historical-votes/?dapil=NonExistentDapil&election_year=1900", 
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_votes_unauthorized(client):
    """Test historical votes endpoints require authentication."""
    response = client.get("/historical-votes/")
    assert response.status_code == 401
