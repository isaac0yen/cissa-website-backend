from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.utils import password_utils
from app.api.v1.auth import schemas
from app.api.models.user import User
from app.api.models.student_profile import StudentProfile
from app.api.repositories.user import UserRepository
from app.api.repositories.student_profile import StudentProfileRepository
from app.utils.logger import logger


class UserService:
    """
    User service class for handling user-related operations.
    This class provides methods for user registration and authentication.
    """

    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.student_profile_repository = StudentProfileRepository(db)

    def register(self, schema: schemas.RegisterRequest) -> User:
        """Creates a new user and student profile (for students)
        Args:
            schema (schemas.RegisterRequest): Registration schema
        Returns:
            User: User object for the newly created user
        """
        # check if user with email already exists
        if self.repository.get_by_email(schema.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists!",
            )

        # Hash password
        hashed_password = password_utils.hash_password(password=schema.password)

        # Create user with student role (default)
        user = User(
            username=schema.username,
            email=schema.email,
            password=hashed_password,
            role="student",
        )

        logger.info(f"Creating user with email: {user.email}")
        created_user = self.repository.create(user)

        # Create student profile for student users
        if created_user.role == "student":
            student_profile = StudentProfile(
                user_id=created_user.id,
                first_name=schema.first_name,
                last_name=schema.last_name,
            )
            self.student_profile_repository.create(student_profile)
            logger.info(f"Created student profile for user: {created_user.id}")

        return created_user

    def authenticate(self, schema: schemas.LoginRequest) -> User:
        """Authenticates a registered user
        Args:
            schema (schemas.LoginRequest): Login Request schema
        Returns:
            User: Authenticated user
        """
        # check if user with the email exists
        user = self.repository.get_by_email(schema.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email",
            )

        if not password_utils.verify_password(schema.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password",
            )

        logger.info(f"User authenticated with email: {user.email}")
        return user
