from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_unregister_participant_removes_email():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    refresh = client.get("/activities")
    assert email not in refresh.json()[activity_name]["participants"]


def test_unregister_missing_participant_returns_error():
    activity_name = "Programming Class"
    email = "missing@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()
