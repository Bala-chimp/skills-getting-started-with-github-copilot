from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index(client):
    expected_location = "/static/index.html"

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details(client):
    activity_name = "Chess Club"

    response = client.get("/activities")

    activity = response.json()[activity_name]
    assert response.status_code == 200
    assert activity["description"] == "Learn strategies and compete in chess tournaments"
    assert activity["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert activity["max_participants"] == 12
    assert activity["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    activity_name = "Soccer Club"
    email = "student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }


def test_signup_rejects_unknown_activity(client):
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from {activity_name}"
    }
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_rejects_unknown_activity(client):
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_rejects_missing_participant(client):
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}