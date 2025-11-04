import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "participants" in activities["Chess Club"]
    assert isinstance(activities["Chess Club"]["participants"], list)

def test_signup_success():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == f"Signed up {email} for {activity_name}"

    # Verify the student was actually added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is already registered
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    response_data = response.json()
    assert "already signed up" in response_data["detail"]

def test_signup_nonexistent_activity():
    activity_name = "NonexistentClub"
    email = "student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    response_data = response.json()
    assert "not found" in response_data["detail"]

def test_unregister_success():
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"  # This email is already registered
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == f"Unregistered {email} from {activity_name}"

    # Verify the student was actually removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    response_data = response.json()
    assert "not registered" in response_data["detail"]

def test_unregister_nonexistent_activity():
    activity_name = "NonexistentClub"
    email = "student@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    response_data = response.json()
    assert "not found" in response_data["detail"]