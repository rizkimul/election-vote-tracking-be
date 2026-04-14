from app.models import RefreshToken

def test_login_returns_refresh_token(client, test_user):
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_refresh_token_flow(client, test_user):
    # 1. Login to get tokens
    login_res = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    refresh_token = login_res.json()["refresh_token"]
    old_access_token = login_res.json()["access_token"]
    
    import time
    time.sleep(2)
    
    # 2. Use refresh token to get new access token
    response = client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] != old_access_token
    # In our implementation, we return the same refresh_token (no rotation yet)
    assert "refresh_token" in data

def test_invalid_refresh_token(client):
    response = client.post("/auth/refresh", json={
        "refresh_token": "invalid-uuid-token"
    })
    assert response.status_code == 401

def test_logout_revokes_token(client, test_user, db_session):
    # 1. Login
    login_res = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    refresh_token = login_res.json()["refresh_token"]
    
    # 2. Logout
    logout_res = client.post("/auth/logout", json={
        "refresh_token": refresh_token
    })
    assert logout_res.status_code == 200
    
    # VP: Check DB
    db_token = db_session.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    assert db_token.revoked is True
    
    # 3. Try to refresh again (should fail)
    refresh_res = client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_res.status_code == 401
