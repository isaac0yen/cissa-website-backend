from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.models.student_test_registration import StudentTestRegistration
from app.api.repositories.registration import RegistrationRepository
from app.api.repositories.student_profile import StudentProfileRepository
from app.api.repositories.test import TestRepository
from app.core.base.schema import PaginatedResponse
from app.utils.logger import logger


class RegistrationService:
    """
    Registration service for handling student test registration operations.
    Provides methods for creating and managing test registrations without payment.
    """

    def __init__(self, db: Session):
        self.repository = RegistrationRepository(db)
        self.test_repository = TestRepository(db)
        self.student_profile_repository = StudentProfileRepository(db)

    def __get_student_profile(self, user_id: str):
        """Get student profile by user ID.

        Args:
            user_id (str): The user's ID

        Returns:
            StudentProfile: The student profile object

        Raises:
            HTTPException: If student profile not found
        """
        profile = self.student_profile_repository.get_by_user_id(user_id)
        if not profile:
            logger.error(f"Student profile not found for user_id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found",
            )
        return profile

    def create_registration(
        self, user_id: str, test_id: str
    ) -> StudentTestRegistration:
        """Create a new test registration for a student.

        Args:
            user_id (str): The user's ID
            test_id (str): The test's ID

        Returns:
            StudentTestRegistration: The created registration

        Raises:
            HTTPException: If validation fails
        """

        student = self.__get_student_profile(user_id)
        student_id = student.id

        # Validate test exists and is published
        test = self.test_repository.get(test_id)
        if not test:
            logger.error(f"Test not found: {test_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found",
            )

        if not test.is_published:
            logger.error(f"Attempted registration for unpublished test: {test_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot register for unpublished test",
            )

        # Check for duplicate registration
        existing = self.repository.get_by_student_and_test(student_id, test_id)
        if existing:
            logger.error(f"Student {student_id} already registered for test {test_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You are already registered for this test",
            )

        # Create registration
        try:
            registration = StudentTestRegistration(
                student_id=student_id,
                test_id=test_id,
                payment_id=None,  # No payment for direct registration
            )

            logger.info(
                f"Creating registration for student {student_id}, test {test_id}"
            )
            return self.repository.create(registration)

        except Exception as e:
            logger.error(f"Error creating registration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the registration",
            )

    def get_my_registrations(
        self, user_id: str, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse:
        """Get paginated list of registrations for a student.

        Args:
            user_id (str): The user's ID
            page (int): Page number
            page_size (int): Items per page

        Returns:
            PaginatedResponse: Paginated registration data
        """

        student = self.__get_student_profile(user_id)
        student_id = student.id

        query = self.repository.base_query()

        query = self.repository.filter_by_student_id(query, student_id)

        # Sort by created_at descending (newest first)
        query = query.order_by(StudentTestRegistration.created_at.desc())

        return self.repository.paginate(query, page, page_size)

    def get_registration_details(
        self, registration_id: str, user_id: str
    ) -> StudentTestRegistration:
        """Get registration details with ownership verification.

        Args:
            registration_id (str): The registration ID
            user_id (str): The user's ID (for ownership check)

        Returns:
            StudentTestRegistration: The registration

        Raises:
            HTTPException: If not found or not owned by student
        """

        student = self.__get_student_profile(user_id)
        student_id = student.id

        registration = self.repository.get(registration_id)

        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration not found",
            )

        # Verify ownership
        if registration.student_id != student_id:
            logger.warning(
                f"Student {student_id} attempted to access registration {registration_id} "
                f"owned by {registration.student_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this registration",
            )

        return registration

    def delete_registration(self, registration_id: str, user_id: str) -> bool:
        """Delete a registration (unregister from test).

        Args:
            registration_id (str): The registration ID
            user_id (str): The user's ID (for ownership check)

        Returns:
            bool: True if deleted successfully

        Raises:
            HTTPException: If not found or not owned by student
        """

        student = self.__get_student_profile(user_id)
        student_id = student.id

        registration = self.repository.get(registration_id)

        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration not found",
            )

        # Verify ownership
        if registration.student_id != student_id:
            logger.warning(
                f"Student {student_id} attempted to delete registration {registration_id} "
                f"owned by {registration.student_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this registration",
            )

        try:
            logger.info(f"Deleting registration {registration_id}")
            return self.repository.delete(registration_id)
        except Exception as e:
            logger.error(f"Error deleting registration {registration_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the registration",
            )
