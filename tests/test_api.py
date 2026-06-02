from datetime import datetime, timedelta, timezone

def test_health_check(client):
    """Test that the health endpoint returns healthy."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_create_event(client, auth_headers):
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

    response = client.post("/api/events", json=event_data, headers=auth_headers)

    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["title"] == event_data["title"]

def test_get_events(client, created_event):
    """Test retrieving the list of events."""
    response = client.get("/api/events")
    
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 1
    assert any(event["id"] == created_event for event in response.json)

def test_get_single_event(client, created_event):
    """Test retrieving a single event by ID."""
    response = client.get(f"/api/events/{created_event}")
    
    assert response.status_code == 200
    assert response.json["id"] == created_event
    assert "title" in response.json

def test_create_rsvp(client, auth_headers, created_event):
    """Test RSVPing to an event."""
    rsvp_data = {"attending": True}
    
    response = client.post(f"/api/rsvps/event/{created_event}", json=rsvp_data, headers=auth_headers)
    
    assert response.status_code == 201
    assert response.json["event_id"] == created_event
    assert response.json["attending"] == True

def test_get_rsvps(client, auth_headers, created_event):
    """Test retrieving RSVPs for an event."""
    # First, create an RSVP
    client.post(f"/api/rsvps/event/{created_event}", json={"attending": True}, headers=auth_headers)
    
    # Then get the RSVPs
    response = client.get(f"/api/rsvps/event/{created_event}")
    
    assert response.status_code == 200
    assert "rsvps" in response.json
    assert "stats" in response.json
    assert response.json["stats"]["attending"] >= 1

def test_create_poll_with_auth(client, auth_headers):
    """Test creating a poll with an authorized user."""
    poll_data = {
        "question": "What do you like better Coffee or Tea?",
        "options": ["Tea", "Coffee"],
        "is_public": True,
        "requires_admin": False
    }
    
    response = client.post("/api/polls", json=poll_data, headers=auth_headers)
    
    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["question"] == poll_data["question"]

# --- Error Scenario Tests ---

def test_duplicate_user_registration(client):
    """Test that registering the same username twice returns a 400 error."""
    user_data = {"username": "duplicate_user", "password": "password"}
    
    # First registration should succeed
    response1 = client.post("/api/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with the same data should fail
    response2 = client.post("/api/auth/register", json=user_data)
    assert response2.status_code == 400
    assert "error" in response2.json

def test_create_event_unauthorized(client):
    """Test creating an event without a token returns 401."""
    event_data = {
        "title": "Unauthorized Event", 
        "date": "2024-01-01T12:00:00Z"
    }
    response = client.post("/api/events", json=event_data)
    assert response.status_code == 401

def test_rsvp_private_event_unauthorized(client, created_private_event):
    """Test RSVPing to a private event without authentication returns 401."""
    rsvp_data = {"attending": True}
    
    # Attempt to RSVP without sending auth_headers
    response = client.post(f"/api/rsvps/event/{created_private_event}", json=rsvp_data)
    
    assert response.status_code == 401
    assert "error" in response.json

def test_create_event_missing_fields(client, auth_headers):
    """Test creating an event with missing required fields returns 400."""
    # Missing title
    event_data_no_title = {"date": "2024-01-01T12:00:00Z"}
    response = client.post("/api/events", json=event_data_no_title, headers=auth_headers)
    assert response.status_code == 400

    # Missing date
    event_data_no_date = {"title": "No Date Event"}
    response = client.post("/api/events", json=event_data_no_date, headers=auth_headers)
    assert response.status_code == 400

def test_create_event_invalid_data(client, auth_headers):
    """Test creating an event with invalid date format returns 400."""
    event_data = {
        "title": "Invalid Date", 
        "date": "not-a-valid-date"
    }
    response = client.post("/api/events", json=event_data, headers=auth_headers)
    assert response.status_code == 400

def test_get_nonexistent_event(client):
    """Test retrieving an event that doesn't exist returns 404."""
    response = client.get("/api/events/99999")
    assert response.status_code == 404

def test_rsvp_nonexistent_event(client, auth_headers):
    """Test RSVPing to a non-existent event returns 404."""
    response = client.post("/api/rsvps/event/99999", json={"attending": True}, headers=auth_headers)
    assert response.status_code == 404