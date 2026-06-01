from app import create_app
import pytest

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test that the health endpoint returns healthy."""
    # arrange
    # act
    response = client.get("/api/health")
    # assert
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}