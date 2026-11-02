import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Mondays",
            "max_participants": 18,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)
    with TestClient(app_module.app) as test_client:
        yield test_client, activities


def test_get_activities_returns_available_activities(client):
    # Arrange
    test_client, activities = client

    # Act
    response = test_client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client):
    # Arrange
    test_client, activities = client
    email = "student@mergington.edu"

    # Act
    response = test_client.post(
        "/activities/Art Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert activities["Art Club"]["participants"] == [email]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    test_client, activities = client
    original_participants = activities["Art Club"]["participants"].copy()

    # Act
    response = test_client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities["Art Club"]["participants"] == original_participants


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    test_client, activities = client
    original_participants = activities["Chess Club"]["participants"].copy()

    # Act
    response = test_client.post(
        "/activities/Chess Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activities["Chess Club"]["participants"] == original_participants


def test_signup_requires_email(client):
    # Arrange
    test_client, activities = client
    original_participants = activities["Art Club"]["participants"].copy()

    # Act
    response = test_client.post("/activities/Art Club/signup")

    # Assert
    assert response.status_code == 422
    assert activities["Art Club"]["participants"] == original_participants


def test_unregister_removes_participant(client):
    # Arrange
    test_client, activities = client
    email = "existing@mergington.edu"

    # Act
    response = test_client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert activities["Chess Club"]["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    test_client, activities = client
    original_participants = activities["Chess Club"]["participants"].copy()

    # Act
    response = test_client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities["Chess Club"]["participants"] == original_participants


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    test_client, activities = client
    original_participants = activities["Art Club"]["participants"].copy()

    # Act
    response = test_client.delete(
        "/activities/Art Club/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert activities["Art Club"]["participants"] == original_participants


def test_unregister_requires_email(client):
    # Arrange
    test_client, activities = client
    original_participants = activities["Chess Club"]["participants"].copy()

    # Act
    response = test_client.delete("/activities/Chess Club/signup")

    # Assert
    assert response.status_code == 422
    assert activities["Chess Club"]["participants"] == original_participants
