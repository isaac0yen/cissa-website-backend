"""Tests for student profile management endpoints"""

from uuid import uuid4
import pytest
from fastapi import status


@pytest.fixture
def student_token(client):
    """Fixture to create a student and return access token"""
    email = f"student_{uuid4().hex}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Testpass123!",
            "username": f"student_{uuid4().hex[:8]}",
            "first_name": "Test",
            "last_name": "Student",
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_user(db_session):
    """Fixture to create an admin user directly in database"""
    from app.api.models.user import User
    from app.utils.password_utils import hash_password

    admin = User(
        username="admin",
        email=f"admin_{uuid4().hex}@example.com",
        password=hash_password("AdminPass123!"),
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def admin_token(client, admin_user):
    """Fixture to get admin access token"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "AdminPass123!"},
    )
    return response.json()["access_token"]


class TestGetStudentProfile:
    """Test getting student profile"""

    def test_student_can_get_own_profile(self, client, student_token):
        """Test that student can retrieve their own profile"""
        response = client.get(
            "/api/v1/student/profile",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status_code"] == 200
        assert "data" in data
        assert data["data"]["first_name"] == "Test"
        assert data["data"]["last_name"] == "Student"

    def test_unauthenticated_cannot_get_profile(self, client):
        """Test that unauthenticated users cannot access profile"""
        response = client.get("/api/v1/student/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_cannot_get_student_profile(self, client, admin_token):
        """Test that admin users cannot access student profile endpoint"""
        response = client.get(
            "/api/v1/student/profile",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_data = response.json()
        error_msg = response_data.get("detail", response_data.get("message", ""))
        assert "Student access required" in error_msg


class TestUpdateStudentProfile:
    """Test updating student profile"""

    def test_student_can_update_own_profile(self, client, student_token):
        """Test that student can update their own profile"""
        update_data = {"first_name": "Updated", "last_name": "Name"}

        response = client.put(
            "/api/v1/student/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["data"]["first_name"] == "Updated"
        assert data["data"]["last_name"] == "Name"

    def test_update_validates_field_length(self, client, student_token):
        """Test that update validates maximum field length"""
        update_data = {
            "first_name": "A" * 101,  # Exceeds max_length=100
            "last_name": "Name",
        }

        response = client.put(
            "/api/v1/student/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_admin_cannot_update_student_profile(self, client, admin_token):
        """Test that admin users cannot update student profile endpoint"""
        update_data = {"first_name": "Updated", "last_name": "Name"}

        response = client.put(
            "/api/v1/student/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_update_profile(self, client):
        """Test that unauthenticated users cannot update profile"""
        update_data = {"first_name": "Updated", "last_name": "Name"}

        response = client.put("/api/v1/student/profile", json=update_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestProfilePersistence:
    """Test that profile changes persist across requests"""

    def test_profile_updates_persist(self, client, student_token):
        """Test that profile updates are saved correctly"""
        # Update profile
        update_data = {"first_name": "Persistent", "last_name": "Data"}
        client.put(
            "/api/v1/student/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {student_token}"},
        )

        # Get profile again
        response = client.get(
            "/api/v1/student/profile",
            headers={"Authorization": f"Bearer {student_token}"},
        )

        data = response.json()
        assert data["data"]["first_name"] == "Persistent"
        assert data["data"]["last_name"] == "Data"
