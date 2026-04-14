
from fastapi.testclient import TestClient
from app.main import app
from jose import jwt
from app.config import JWT_SECRET, JWT_ALGO
import time

from app.deps import get_current_user

client = TestClient(app)

# Mock user object
class MockUser:
    def __init__(self):
        self.id = 1
        self.username = "testuser"

def override_get_current_user():
    return MockUser()

app.dependency_overrides[get_current_user] = override_get_current_user

def get_auth_headers():
    return {"Authorization": "Bearer mock_token"}

def test_crud_activity_type():
    headers = get_auth_headers()
    
    # 1. Create
    payload = {"name": "Test Activity", "max_participants": 50}
    response = client.post("/activity-types/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Activity"
    assert data["max_participants"] == 50
    item_id = data["id"]

    # 2. Read (List)
    response = client.get("/activity-types/", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert any(item["id"] == item_id for item in items)

    # 3. Update
    update_payload = {"name": "Test Activity Updated", "max_participants": 75}
    response = client.put(f"/activity-types/{item_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["name"] == "Test Activity Updated"
    assert updated_data["max_participants"] == 75
    assert updated_data["id"] == item_id

    # 4. Verify Update in List
    response = client.get("/activity-types/", headers=headers)
    items = response.json()
    updated_item = next(item for item in items if item["id"] == item_id)
    assert updated_item["name"] == "Test Activity Updated"
    assert updated_item["max_participants"] == 75

    # 5. Delete
    response = client.delete(f"/activity-types/{item_id}", headers=headers)
    assert response.status_code == 200

    # 6. Verify Delete
    response = client.get("/activity-types/", headers=headers)
    items = response.json()
    assert not any(item["id"] == item_id for item in items)
