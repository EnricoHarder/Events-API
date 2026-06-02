from datetime import datetime, timedelta, timezone
import uuid

def get_unique_username():
    """Helper to generate a unique username for each test run."""
    return f"user_{uuid.uuid4().hex[:8]}"

def test_health_check(api_client):
    """Test that the health endpoint returns healthy."""
    response = api_client.get("/api/health")
    assert response.status_code == 200
    
    # The response object from 'requests' and 'test_client' have different ways to access json
    json_data = response.json() if callable(response.json) else response.json
    assert json_data == {"status": "healthy"}

def test_create_event(api_client, auth_headers):
    """Test that a new event can be created with a valid token."""
    event_date = datetime.now(timezone.utc) + timedelta(days=10)
    event_data = {
        "title": "My Test Event",
        "description": "A cool event.",
        "date": event_date.isoformat(),
        "location": "Cyberspace",
        "capacity": 100,
        "is_public": True
    }

    response = api_client.post("/api/events", json=event_data, headers=auth_headers)

    assert response.status_code == 201
    json_data = response.json() if callable(response.json) else response.json
    assert "id" in json_data
    assert json_data["title"] == event_data["title"]

def test_get_events(api_client, created_event):
    """Test retrieving the list of events."""
    response = api_client.get("/api/events")
    
    assert response.status_code == 200
    json_data = response.json() if callable(response.json) else response.json
    assert isinstance(json_data, list)
    assert len(json_data) >= 1
    assert any(event["id"] == created_event for event in json_data)

def test_get_single_event(api_client, created_event):
    """Test retrieving a single event by ID."""
    response = api_client.get(f"/api/events/{created_event}")
    
    assert response.status_code == 200
    json_data = response.json() if callable(response.json) else response.json
    assert json_data["id"] == created_event
    assert "title" in json_data

def test_create_rsvp(api_client, auth_headers, created_event):
    """Test RSVPing to an event."""
    rsvp_data = {"attending": True}
    
    response = api_client.post(f"/api/rsvps/event/{created_event}", json=rsvp_data, headers=auth_headers)
    
    assert response.status_code == 201
    json_data = response.json() if callable(response.json) else response.json
    assert json_data["event_id"] == created_event
    assert json_data["attending"] == True

def test_get_rsvps(api_client, auth_headers, created_event):
    """Test retrieving RSVPs for an event."""
    # First, create an RSVP
    api_client.post(f"/api/rsvps/event/{created_event}", json={"attending": True}, headers=auth_headers)
    
    # Then get the RSVPs
    response = api_client.get(f"/api/rsvps/event/{created_event}")
    
    assert response.status_code == 200
    json_data = response.json() if callable(response.json) else response.json
    assert "rsvps" in json_data
    assert "stats" in json_data
    assert json_data["stats"]["attending"] >= 1

def test_create_poll_with_auth(api_client, auth_headers):
    """Test creating a poll with an authorized user."""
    poll_data = {
        "question": "What do you like better Coffee or Tea?",
        "options": ["Tea", "Coffee"],
        "is_public": True,
        "requires_admin": False
    }
    
    response = api_client.post("/api/polls", json=poll_data, headers=auth_headers)
    
    assert response.status_code == 201
    json_data = response.json() if callable(response.json) else response.json
    assert "id" in json_data
    assert json_data["question"] == poll_data["question"]

# --- Error Scenario Tests ---

def test_duplicate_user_registration(api_client):
    """Test that registering the same username twice returns a 400 error."""
    # Use a highly unique username for this specific test so it doesn't conflict across runs
    unique_username = get_unique_username()
    user_data = {"username": unique_username, "password": "password"}
    
    # First registration should succeed
    response1 = api_client.post("/api/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with the exact same username should fail
    response2 = api_client.post("/api/auth/register", json=user_data)
    assert response2.status_code == 400
    json_data = response2.json() if callable(response2.json) else response2.json
    assert "error" in json_data

def test_create_event_unauthorized(api_client):
    """Test creating an event without a token returns 401."""
    event_data = {
        "title": "Unauthorized Event", 
        "date": "2024-01-01T12:00:00Z"
    }
    response = api_client.post("/api/events", json=event_data)
    assert response.status_code == 401

def test_rsvp_private_event_unauthorized(api_client, created_private_event):
    """Test RSVPing to a private event without authentication returns 401."""
    rsvp_data = {"attending": True}
    
    # Attempt to RSVP without sending auth_headers
    response = api_client.post(f"/api/rsvps/event/{created_private_event}", json=rsvp_data)
    
    assert response.status_code == 401
    json_data = response.json() if callable(response.json) else response.json
    assert "error" in json_data

def test_create_event_missing_fields(api_client, auth_headers):
    """Test creating an event with missing required fields returns 400."""
    # Missing title
    event_data_no_title = {"date": "2024-01-01T12:00:00Z"}
    response = api_client.post("/api/events", json=event_data_no_title, headers=auth_headers)
    assert response.status_code == 400

    # Missing date
    event_data_no_date = {"title": "No Date Event"}
    response = api_client.post("/api/events", json=event_data_no_date, headers=auth_headers)
    assert response.status_code == 400

def test_create_event_invalid_data(api_client, auth_headers):
    """Test creating an event with invalid date format returns 400."""
    event_data = {
        "title": "Invalid Date", 
        "date": "not-a-valid-date"
    }
    response = api_client.post("/api/events", json=event_data, headers=auth_headers)
    assert response.status_code == 400

def test_get_nonexistent_event(api_client):
    """Test retrieving an event that doesn't exist returns 404."""
    response = api_client.get("/api/events/99999")
    assert response.status_code == 404

def test_rsvp_nonexistent_event(api_client, auth_headers):
    """Test RSVPing to a non-existent event returns 404."""
    response = api_client.post("/api/rsvps/event/99999", json={"attending": True}, headers=auth_headers)
    assert response.status_code == 404