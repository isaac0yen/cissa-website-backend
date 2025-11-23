from sqlalchemy.orm import Session
from app.core.base.repository import BaseRepository
from app.api.models.student_profile import StudentProfile


class StudentProfileRepository(BaseRepository[StudentProfile]):
    """
    StudentProfile repository class for CRUD operations on StudentProfile model.
    This class inherits from BaseRepository and provides specific methods for StudentProfile model.
    Attributes:
        model (Type[StudentProfile]): The SQLAlchemy StudentProfile model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(StudentProfile, db)

    def get_by_user_id(self, user_id: str) -> StudentProfile:
        """Get a student profile by user_id.

        Args:
            user_id (str): The ID of the user.

        Returns:
            StudentProfile: The student profile object if found, None otherwise.
        """
        return self.db.query(self.model).filter(self.model.user_id == user_id).first()
