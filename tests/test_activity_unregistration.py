from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

ORIGINAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture
def client():
    app_module.activities = deepcopy(ORIGINAL_ACTIVITIES)
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_list(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_for_activity_adds_student(client):
    activity_name = "Basketball Team"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_unregister_participant_removes_email(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_missing_participant_returns_error(client):
    activity_name = "Programming Class"
    email = "missing@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()


def test_invalid_activity_returns_not_found(client):
    response = client.post("/activities/Not Real/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
