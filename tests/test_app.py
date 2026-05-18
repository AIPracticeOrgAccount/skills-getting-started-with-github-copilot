from urllib.parse import quote

from fastapi import status


def test_root_redirects_to_static_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_for_activity_returns_400_for_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@student.mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"
    client.post(url, params={"email": email})

    # Act
    duplicate_response = client.post(url, params={"email": email})

    # Assert
    assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST
    assert duplicate_response.json()["detail"] == "Student already signed up"


def test_unregister_from_activity_removes_participant(client):
    # Arrange
    activity_name = "Programming Class"
    email = "withdraw@student.mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup"
    unregister_url = f"/activities/{quote(activity_name)}/participants"
    client.post(signup_url, params={"email": email})

    # Act
    response = client.delete(unregister_url, params={"email": email})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregistering_nonexistent_participant_returns_404(client):
    # Arrange
    activity_name = "Drama Club"
    email = "missing@student.mergington.edu"
    unregister_url = f"/activities/{quote(activity_name)}/participants"

    # Act
    response = client.delete(unregister_url, params={"email": email})

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Participant not found"
