from sqlalchemy.orm import Session, Query

from app.core.base.repository import BaseRepository
from app.api.models.student_test_registration import StudentTestRegistration


class RegistrationRepository(BaseRepository[StudentTestRegistration]):
    """
    Registration repository for CRUD operations on StudentTestRegistration model.
    """

    def __init__(self, db: Session):
        super().__init__(StudentTestRegistration, db)

    def get_by_student_and_test(
        self, student_id: str, test_id: str
    ) -> StudentTestRegistration | None:
        """Get registration by student and test ID.

        Args:
            student_id (str): The student's ID
            test_id (str): The test's ID

        Returns:
            StudentTestRegistration | None: Registration if found, None otherwise
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.student_id == student_id,
                self.model.test_id == test_id,
            )
            .first()
        )

    def get_student_registrations(
        self, student_id: str
    ) -> list[StudentTestRegistration]:
        """Get all registrations for a student.

        Args:
            student_id (str): The student's ID

        Returns:
            list[StudentTestRegistration]: List of registrations
        """
        return (
            self.db.query(self.model).filter(self.model.student_id == student_id).all()
        )

    def filter_by_test_id(
        self, query: Query[StudentTestRegistration], test_id: str
    ) -> Query[StudentTestRegistration]:
        """Filter registrations by test ID.

        Args:
            query: The base query to filter
            test_id: The test ID to filter by

        Returns:
            Query: Filtered query
        """
        return query.filter(self.model.test_id == test_id)

    def filter_by_student_id(
        self, query: Query[StudentTestRegistration], student_id: str
    ) -> Query[StudentTestRegistration]:
        """Filter registrations by student ID.

        Args:
            query: The base query to filter
            student_id: The student ID to filter by

        Returns:
            Query: Filtered query
        """
        return query.filter(self.model.student_id == student_id)