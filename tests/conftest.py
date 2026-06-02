import pytest
import os
from datetime import datetime, timedelta, timezone
from app import create_app
from models import db
import requests

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'a-secure-and-long-enough-secret-key-for-testing'

@pytest.fixture(scope='session')
def base_url():
    """Fixture to define the base URL for API tests."""
    return os.environ.get('API_BASE_URL', 'http://127.0.0.1:5000')

@pytest.fixture(scope='module')
def app():
    """Create a Flask app for testing with an in-memory database."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def api_client(base_url, test_client):
    """
    Fixture to provide a client for API tests.
    Uses a real requests session if API_BASE_URL is set,
    otherwise uses the Flask test client.
    """
    if os.environ.get('API_BASE_URL'):
        # E2E test against a running server
        session = requests.Session()
        session.base_url = base_url
        
        # Add post, get, etc. methods to the session object to mimic the test client
        def make_request(method):
            def request_wrapper(url, **kwargs):
                return session.request(method, f"{base_url}{url}", **kwargs)
            return request_wrapper

        session.get = make_request('GET')
        session.post = make_request('POST')
        session.put = make_request('PUT')
        session.delete = make_request('DELETE')
        
        return session
    else:
        # Integration test using the Flask test client
        return test_client

@pytest.fixture
def auth_headers(api_client):
    """Fixture to provide authentication headers for a test user."""
    # Use a unique username to avoid conflicts between tests
    username = f"testuser_{datetime.now().timestamp()}"
    
    # Send registration request
    reg_response = api_client.post("/api/auth/register", json={"username": username, "password": "password"})
    reg_data = reg_response.json() if callable(reg_response.json) else reg_response.json
    
    # If registration failed (e.g. user exists in a persistent DB), we still try to login
    # This is important when running E2E tests against a real server where the DB isn't wiped
    
    login_response = api_client.post("/api/auth/login", json={"username": username, "password": "password"})
    login_data = login_response.json() if callable(login_response.json) else login_response.json
    
    if "access_token" not in login_data:
        raise ValueError(f"Failed to get access token. Login response: {login_data}, Reg response: {reg_data}")
        
    token = login_data["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def created_event(api_client, auth_headers):
    """Fixture to create a base public event and return its ID."""
    event_date = datetime.now(timezone.utc) + timedelta(days=10)
    event_data = {
        "title": "Base Public Test Event",
        "date": event_date.isoformat(),
        "capacity": 10
    }
    response = api_client.post("/api/events", json=event_data, headers=auth_headers)
    json_data = response.json() if callable(response.json) else response.json
    return json_data["id"]

@pytest.fixture
def created_private_event(api_client, auth_headers):
    """Fixture to create a private event and return its ID."""
    event_date = datetime.now(timezone.utc) + timedelta(days=10)
    event_data = {
        "title": "Private Test Event",
        "date": event_date.isoformat(),
        "is_public": False
    }
    response = api_client.post("/api/events", json=event_data, headers=auth_headers)
    json_data = response.json() if callable(response.json) else response.json
    return json_data["id"]