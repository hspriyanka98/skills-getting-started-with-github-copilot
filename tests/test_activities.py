import pytest
from fastapi import status


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_all_activities(self, client, reset_activities):
        """Test retrieving all activities - AAA pattern"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        assert len(activities) == 3
        assert all(activity in activities for activity in expected_activities)

    def test_get_activity_details(self, client, reset_activities):
        """Test that activity details are correctly returned - AAA pattern"""
        # Arrange
        expected_keys = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        chess_club = activities["Chess Club"]
        assert all(key in chess_club for key in expected_keys)
        assert chess_club["max_participants"] == 12
        assert chess_club["participants"] == []


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity - AAA pattern"""
        # Arrange
        activity_name = "Chess Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple students can signup for same activity - AAA pattern"""
        # Arrange
        activity_name = "Programming Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act
        response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        response2 = client.post(f"/activities/{activity_name}/signup", params={"email": email2})

        # Assert
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 2

    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup is rejected - AAA pattern"""
        # Arrange
        activity_name = "Chess Club"
        email = "student@mergington.edu"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity - AAA pattern"""
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration - AAA pattern"""
        # Arrange
        activity_name = "Chess Club"
        email = "student@mergington.edu"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "Unregistered" in response.json()["message"]
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistration for student not in activity - AAA pattern"""
        # Arrange
        activity_name = "Chess Club"
        email = "not_registered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from non-existent activity - AAA pattern"""
        # Arrange
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_one_of_many_participants(self, client, reset_activities):
        """Test unregistering one student doesn't affect others - AAA pattern"""
        # Arrange
        activity_name = "Gym Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email1}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 not in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]
