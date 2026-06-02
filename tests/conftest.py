import pytest
from datetime import datetime, timedelta, timezone
from app import create_app
from models import db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'a-secure-and-long-enough-secret-key-for-testing'

@pytest.fixture
def app():
    """Create a Flask app for testing with an in-memory database."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Fixture to provide authentication headers for a test user."""
    # Use a unique username to avoid conflicts between tests
    username = f"testuser_{datetime.now().timestamp()}"
    client.post("/api/auth/register", json={"username": username, "password": "password"})
    response = client.post("/api/auth/login", json={"username": username, "password": "password"})
    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def created_event(client, auth_headers):
    """Fixture to create a base public event and return its ID."""
    event_date = datetime.now(timezone.utc) + timedelta(days=10)
    event_data = {
        "title": "Base Public Test Event",
        "date": event_date.isoformat(),
        "capacity": 10
    }
    response = client.post("/api/events", json=event_data, headers=auth_headers)
    return response.json["id"]

@pytest.fixture
def created_private_event(client, auth_headers):
    """Fixture to create a private event and return its ID."""
    event_date = datetime.now(timezone.utc) + timedelta(days=10)
    event_data = {
        "title": "Private Test Event",
        "date": event_date.isoformat(),
        "is_public": False
    }
    response = client.post("/api/events", json=event_data, headers=auth_headers)
    return response.json["id"]