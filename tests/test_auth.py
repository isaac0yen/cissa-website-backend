from uuid import uuid4
from fastapi import status


class TestStudentRegistration:
    """Test student registration with profile creation"""

    def test_register_student_creates_profile(self, client, db_session):
        """Test that registering creates both User and StudentProfile"""
        email = f"student_{uuid4().hex}@example.com"
        payload = {
            "email": email,
            "password": "Testpass123!",
            "username": "teststudent",
            "first_name": "Test",
            "last_name": "Student",
        }

        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["data"]["email"] == email
        assert data["data"]["username"] == "teststudent"
        assert data["data"]["role"] == "student"
        assert "access_token" in data
        assert "refresh_token" in data

    def test_register_validates_required_fields(self, client):
        """Test that all required fields are validated"""
        # Missing first_name
        payload = {
            "email": "test@example.com",
            "password": "Testpass123!",
            "username": "testuser",
            "last_name": "Student",
        }
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_prevents_duplicate_email(self, client):
        """Test that duplicate email registration is prevented"""
        email = f"duplicate_{uuid4().hex}@example.com"
        payload = {
            "email": email,
            "password": "Testpass123!",
            "username": "user1",
            "first_name": "Test",
            "last_name": "User",
        }

        # First registration
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        # Duplicate registration
        payload["username"] = "user2"  # Different username
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # Check for error message (supports both formats)
        error_msg = response_data.get(
            "detail", response_data.get("message", "")
        ).lower()
        assert "already exists" in error_msg


class TestStudentLogin:
    """Test student login functionality"""

    def test_login_student_returns_role(self, client):
        """Test that login returns user role"""
        email = f"student_{uuid4().hex}@example.com"
        password = "Testpass123!"

        # Register
        client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
            },
        )

        # Login
        response = client.post(
            "/api/v1/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["data"]["email"] == email
        assert data["data"]["role"] == "student"
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_with_invalid_email(self, client):
        """Test login with non-existent email"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_wrong_password(self, client):
        """Test login with incorrect password"""
        email = f"student_{uuid4().hex}@example.com"

        # Register
        client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "CorrectPass123!",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
            },
        )

        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login", json={"email": email, "password": "WrongPass123!"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestTokenRefresh:
    """Test JWT token refresh functionality"""

    def test_refresh_token_success(self, client):
        """Test successful token refresh"""
        email = f"student_{uuid4().hex}@example.com"

        # Register
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "Testpass123!",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        refresh_token = response.json()["refresh_token"]

        # Refresh token
        response = client.post(
            "/api/v1/auth/token/refresh", json={"refresh_token": refresh_token}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()


class TestGetCurrentUser:
    """Test get current user endpoint"""

    def test_get_user_with_valid_token(self, client):
        """Test getting user info with valid access token"""
        email = f"student_{uuid4().hex}@example.com"

        # Register
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "Testpass123!",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        access_token = response.json()["access_token"]

        # Get user
        response = client.get(
            "/api/v1/auth/user", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["email"] == email
        assert data["data"]["role"] == "student"

    def test_get_user_without_token(self, client):
        """Test getting user info without authentication"""
        response = client.get("/api/v1/auth/user")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
