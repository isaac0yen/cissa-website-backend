from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.repositories.student_profile import StudentProfileRepository
from app.api.models.student_profile import StudentProfile
from app.api.v1.student_profile import schemas
from app.utils.logger import logger


class StudentProfileService:
    """
    StudentProfile service class for handling profile-related operations.
    This class provides methods for viewing and updating student profiles.
    """

    def __init__(self, db: Session):
        self.repository = StudentProfileRepository(db)

    def get_profile_by_user_id(self, user_id: str) -> StudentProfile:
        """Get student profile by user ID

        Args:
            user_id: ID of the user

        Returns:
            StudentProfile: Student profile object

        Raises:
            HTTPException: If profile not found
        """
        profile = self.repository.get_by_user_id(user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found",
            )

        return profile

    def update_profile(
        self, user_id: str, schema: schemas.UpdateStudentProfileRequest
    ) -> StudentProfile:
        """Update student profile

        Args:
            user_id: ID of the user
            schema: Update request schema

        Returns:
            StudentProfile: Updated student profile

        Raises:
            HTTPException: If profile not found
        """
        profile = self.get_profile_by_user_id(user_id)

        # Update fields
        profile.first_name = schema.first_name
        profile.last_name = schema.last_name

        updated_profile = self.repository.update(profile)
        logger.info(f"Updated student profile for user: {user_id}")

        return updated_profile
