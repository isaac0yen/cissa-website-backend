"""Tests for announcement and signatory endpoints"""

from uuid import uuid4
import pytest
from fastapi import status


@pytest.fixture
def admin_token(client, db_session):
    """Fixture to get admin access token"""
    from app.api.models.user import User
    from app.utils.password_utils import hash_password

    email = f"admin_{uuid4().hex}@example.com"
    admin = User(
        username=f"admin_{uuid4().hex[:8]}",
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
    return response.json()["access_token"]


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


class TestSignatoryEndpoints:
    """Test signatory CRUD endpoints"""

    def test_admin_can_create_signatory(self, client, admin_token):
        """Test that admin can create a signatory"""
        payload = {
            "name": "John Doe",
            "role": "President",
            "alias": "JD",
            "contact": "+2348012345678",
        }

        response = client.post(
            "/api/v1/signatories/",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["status_code"] == 201
        assert data["data"]["name"] == "John Doe"
        assert data["data"]["role"] == "President"
        assert data["data"]["alias"] == "JD"

    def test_student_cannot_create_signatory(self, client, student_token):
        """Test that students cannot create signatories"""
        payload = {
            "name": "John Doe",
            "role": "President",
            "alias": None,
            "contact": None,
        }

        response = client.post(
            "/api/v1/signatories/",
            json=payload,
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_create_signatory(self, client):
        """Test that unauthenticated users cannot create signatories"""
        payload = {"name": "John Doe", "role": "President"}

        response = client.post("/api/v1/signatories/", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_get_all_signatories(self, client, admin_token, db_session):
        """Test that admin can retrieve all signatories"""
        from app.api.models.announcement import Signatory

        # Create test signatories
        sig1 = Signatory(name="Signatory 1", role="President")
        sig2 = Signatory(name="Signatory 2", role="Vice President")
        db_session.add_all([sig1, sig2])
        db_session.commit()

        response = client.get(
            "/api/v1/signatories/", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert len(data["data"]) >= 2

    def test_admin_can_update_signatory(self, client, admin_token, db_session):
        """Test that admin can update a signatory"""
        from app.api.models.announcement import Signatory

        # Create signatory
        signatory = Signatory(name="Original Name", role="President")
        db_session.add(signatory)
        db_session.commit()

        # Update signatory
        update_payload = {"name": "Updated Name", "role": "Vice President"}

        response = client.put(
            f"/api/v1/signatories/{signatory.id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["role"] == "Vice President"

    def test_admin_can_delete_signatory(self, client, admin_token, db_session):
        """Test that admin can delete a signatory"""
        from app.api.models.announcement import Signatory

        # Create signatory
        signatory = Signatory(name="To Delete", role="President")
        db_session.add(signatory)
        db_session.commit()
        signatory_id = signatory.id

        # Delete signatory
        response = client.delete(
            f"/api/v1/signatories/{signatory_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_student_cannot_delete_signatory(self, client, student_token, db_session):
        """Test that students cannot delete signatories"""
        from app.api.models.announcement import Signatory

        # Create signatory
        signatory = Signatory(name="Protected", role="President")
        db_session.add(signatory)
        db_session.commit()

        response = client.delete(
            f"/api/v1/signatories/{signatory.id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAnnouncementEndpoints:
    """Test announcement CRUD endpoints"""

    def test_public_can_get_all_announcements(self, client):
        """Test that announcements are publicly accessible"""
        response = client.get("/api/v1/announcements/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "data" in data
        assert "total_items" in data["data"]
        assert "items" in data["data"]

    def test_student_cannot_create_announcement(self, client, student_token):
        """Test that students cannot create announcements"""
        from datetime import datetime

        response = client.post(
            "/api/v1/announcements/",
            data={
                "title": "Test",
                "category": "General",
                "body": "Test body",
                "session": "2024/2025",
                "published_at": datetime.now().isoformat(),
                "signatories": "[]",
            },
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAnnouncementWithSignatories:
    """Test announcement endpoints with signatories"""

    def test_announcement_response_structure(self, client):
        """Test that announcement list response has correct structure"""
        response = client.get("/api/v1/announcements/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "data" in data
        assert "items" in data["data"]
        assert isinstance(data["data"]["items"], list)


class TestInputValidation:
    """Test input validation for announcements and signatories"""

    def test_signatory_validates_required_fields(self, client, admin_token):
        """Test that signatory creation validates required fields"""
        # Missing name
        payload = {"role": "President"}

        response = client.post(
            "/api/v1/signatories/",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signatory_validates_field_length(self, client, admin_token):
        """Test that signatory validates maximum field length"""
        payload = {
            "name": "A" * 256,  # Exceeds max_length=255
            "role": "President",
        }

        response = client.post(
            "/api/v1/signatories/",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signatory_accepts_optional_fields(self, client, admin_token):
        """Test that signatory accepts None for optional fields"""
        payload = {
            "name": "Test Signatory",
            "role": "President",
            "alias": None,
            "contact": None,
        }

        response = client.post(
            "/api/v1/signatories/",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["data"]["alias"] is None
        assert data["data"]["contact"] is None
