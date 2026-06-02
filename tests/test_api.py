from app import create_app
import pytest
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def register_and_login(client, username="testuser", password="password"):
    """Helper function to register and login a user, returns the access token."""
    client.post("/api/auth/register", json={"username": username, "password": password})
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    return response.json["access_token"]

def test_health_check(client):
    """Test that the health endpoint returns healthy."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_create_event(client):
    """Test that a new event can be created with a valid token."""
    # Arrange
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    event_date = datetime.utcnow() + timedelta(days=10)
    event_data = {
        "title": "My Test Event",
        "description": "A cool event.",
        "date": event_date.isoformat() + "Z",
        "location": "Cyberspace",
        "capacity": 100,
        "is_public": True
    }

    # Act
    response = client.post("/api/events", json=event_data, headers=headers)

    # Assert
    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["title"] == event_data["title"]
    assert response.json["location"] == event_data["location"]
    assert response.json["created_by"] is not None

def test_create_poll_with_auth(client):
    """Test creating a poll with an authorized user."""
    # Arrange
    token = register_and_login(client, username="polluser", password="password")
    headers = {"Authorization": f"Bearer {token}"}
    poll_data = {
        "question": "What do you like better Coffee or Tea?",
        "options": [
            "Tea",
            "Coffee"
        ],
        "is_public": True,
        "requires_admin": False
    }
    
    # Act
    response = client.post("/api/polls", json=poll_data, headers=headers)
    
    # Assert
    assert response.status_code == 201
    assert "id" in response.json
    for key in ["question", "is_public", "requires_admin"]:
        assert response.json[key] == poll_data[key]

    response_options = sorted([option["text"] for option in response.json["options"]])
    assert response_options == sorted(poll_data["options"])
    assert response.json["requires_admin"] == poll_data["requires_admin"]