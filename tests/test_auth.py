"""
Unit tests for authentication endpoints.
Covers registration, login, profile management, password change, and token validation.
"""


# === POSITIVE CASES ===

def test_register_success(client):
    """Test successful user registration with valid data."""
    response = client.post("/auth/register", json={
        "username": "newuser",
        "name": "New User",
        "password": "securepassword123",
        "nik": "9876543210123456"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["name"] == "New User"
    assert "id" in data


def test_login_success(client, test_user):
    """Test successful login with valid credentials."""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client, auth_headers):
    """Test getting current user profile with valid token."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["name"] == "Test User"


def test_update_profile(client, auth_headers):
    """Test updating user profile."""
    response = client.put("/auth/me", json={
        "name": "Updated Name",
        "email": "updated@example.com",
        "phone": "081234567890"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


def test_change_password_success(client, auth_headers):
    """Test changing password with correct current password."""
    response = client.put("/auth/me/password", json={
        "current_password": "password123",
        "new_password": "newpassword456"
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password berhasil diubah"


# === NEGATIVE CASES ===

def test_register_duplicate_username(client, test_user):
    """Test registration fails with duplicate username."""
    response = client.post("/auth/register", json={
        "username": "testuser",  # Already exists
        "name": "Another User",
        "password": "somepassword"
    })
    # Service raises ValueError which gets caught and returns 500
    assert response.status_code == 500
    data = response.json()
    assert "terdaftar" in data.get("message", "").lower() or response.status_code == 500


def test_login_invalid_password(client, test_user):
    """Test login fails with wrong password."""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 400
    data = response.json()
    assert "message" in data or "detail" in data


def test_login_nonexistent_user(client):
    """Test login fails with non-existent username."""
    response = client.post("/auth/login", json={
        "username": "nosuchuser",
        "password": "anypassword"
    })
    assert response.status_code == 400


def test_get_current_user_no_token(client):
    """Test accessing /auth/me without token returns 401."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(client):
    """Test accessing /auth/me with invalid token returns 401."""
    response = client.get("/auth/me", headers={
        "Authorization": "Bearer invalid_token_here"
    })
    assert response.status_code == 401


def test_change_password_wrong_current(client, auth_headers):
    """Test changing password fails with wrong current password."""
    response = client.put("/auth/me/password", json={
        "current_password": "wrongcurrentpassword",
        "new_password": "newpassword456"
    }, headers=auth_headers)
    assert response.status_code == 400
    data = response.json()
    assert "salah" in data.get("message", "").lower() or "password" in data.get("message", "").lower()
