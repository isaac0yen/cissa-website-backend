"""Tests for Role-Based Access Control (RBAC)"""

from uuid import uuid4
import pytest
from fastapi import status


@pytest.fixture
def student_user_and_token(client):
    """Fixture to create a student user and return user data + token"""
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
    data = response.json()
    return {"user": data["data"], "access_token": data["access_token"]}


@pytest.fixture
def admin_user_and_token(client, db_session):
    """Fixture to create an admin user and return token"""
    from app.api.models.user import User
    from app.utils.password_utils import hash_password

    email = f"admin_{uuid4().hex}@example.com"
    admin = User(
        username="admin",
        email=email,
        password=hash_password("AdminPass123!"),
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()

    # Login to get token
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "AdminPass123!"}
    )
    return {
        "user": {"email": email, "role": "admin"},
        "access_token": response.json()["access_token"],
    }


class TestStudentRBAC:
    """Test student role-based access control"""

    def test_student_has_student_role(self, student_user_and_token):
        """Test that registered users have student role"""
        assert student_user_and_token["user"]["role"] == "student"

    def test_student_can_access_student_endpoints(self, client, student_user_and_token):
        """Test that students can access student-only endpoints"""
        response = client.get(
            "/api/v1/student/profile",
            headers={
                "Authorization": f"Bearer {student_user_and_token['access_token']}"
            },
        )
        assert response.status_code == status.HTTP_200_OK

    def test_student_cannot_access_admin_endpoints(
        self, client, student_user_and_token
    ):
        """Test that students cannot access admin-only endpoints"""
        # Try to create a signatory (admin only)
        response = client.post(
            "/api/v1/signatories/",
            json={
                "name": "Test Signatory",
                "role": "President",
                "alias": None,
                "contact": None,
            },
            headers={
                "Authorization": f"Bearer {student_user_and_token['access_token']}"
            },
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_data = response.json()
        error_msg = response_data.get("detail", response_data.get("message", ""))
        assert "Admin access required" in error_msg


class TestAdminRBAC:
    """Test admin role-based access control"""

    def test_admin_has_admin_role(self, admin_user_and_token):
        """Test that admin users have admin role"""
        assert admin_user_and_token["user"]["role"] == "admin"

    def test_admin_can_access_admin_endpoints(self, client, admin_user_and_token):
        """Test that admins can access admin-only endpoints"""
        response = client.get(
            "/api/v1/signatories/",
            headers={"Authorization": f"Bearer {admin_user_and_token['access_token']}"},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_admin_cannot_access_student_endpoints(self, client, admin_user_and_token):
        """Test that admins cannot access student-only endpoints"""
        response = client.get(
            "/api/v1/student/profile",
            headers={"Authorization": f"Bearer {admin_user_and_token['access_token']}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_data = response.json()
        error_msg = response_data.get("detail", response_data.get("message", ""))
        assert "Student access required" in error_msg


class TestUnauthenticatedAccess:
    """Test access without authentication"""

    def test_unauthenticated_cannot_access_protected_endpoints(self, client):
        """Test that unauthenticated requests are rejected"""
        # Try student endpoint
        response = client.get("/api/v1/student/profile")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Try admin endpoint
        response = client.get("/api/v1/signatories/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected"""
        response = client.get(
            "/api/v1/student/profile", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAnnouncementRBAC:
    """Test RBAC for announcement endpoints"""

    def test_admin_can_create_announcement(self, client, admin_user_and_token):
        """Test that admins can create announcements"""
        # Note: This is a form endpoint, testing with minimal data
        from datetime import datetime

        response = client.post(
            "/api/v1/announcements/",
            data={
                "title": "Test Announcement",
                "category": "General",
                "body": "Test body",
                "session": "2024/2025",
                "published_at": datetime.now().isoformat(),
                "signatories": "[]",
            },
            headers={"Authorization": f"Bearer {admin_user_and_token['access_token']}"},
        )
        # May fail due to image requirement, but should not be 403
        assert response.status_code != status.HTTP_403_FORBIDDEN

    def test_student_cannot_create_announcement(self, client, student_user_and_token):
        """Test that students cannot create announcements"""
        from datetime import datetime

        response = client.post(
            "/api/v1/announcements/",
            data={
                "title": "Test Announcement",
                "category": "General",
                "body": "Test body",
                "session": "2024/2025",
                "published_at": datetime.now().isoformat(),
                "signatories": "[]",
            },
            headers={
                "Authorization": f"Bearer {student_user_and_token['access_token']}"
            },
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_public_can_view_announcements(self, client):
        """Test that announcements are publicly viewable"""
        response = client.get("/api/v1/announcements/")
        assert response.status_code == status.HTTP_200_OK
