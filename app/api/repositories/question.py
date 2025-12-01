from sqlalchemy.orm import Session, Query

from app.core.base.repository import BaseRepository
from app.api.models.test import Question, QuestionOption


class QuestionRepository(BaseRepository[Question]):
    """
    Question repository class for CRUD operations on Question model.
    This class inherits from BaseRepository and provides specific methods for Question model.
    Attributes:
        model (Type[Question]): The SQLAlchemy Question model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(Question, db)

    def filter_by_test_id(
        self, query: Query[Question], test_id: str
    ) -> Query[Question]:
        """Filter questions by test_id.
        Args:
            query (Query[Question]): The base query to filter.
            test_id (str): The test_id to filter by.
        Returns:
            Query[Question]: The filtered query.
        """
        return query.filter(self.model.test_id == test_id)

class QuestionOptionRepository(BaseRepository[QuestionOption]):
    """
    QuestionOption repository class for CRUD operations on QuestionOption model.
    This class inherits from BaseRepository and provides specific methods for QuestionOption model.
    Attributes:
        model (Type[QuestionOption]): The SQLAlchemy QuestionOption model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(QuestionOption, db)

    def get_by_question_id(self, question_id: str) -> list[QuestionOption]:
        """Get question options by question_id.
        Args:
            question_id (str): The question_id to filter by.
        Returns:
            list[QuestionOption]: List of QuestionOption objects.
        """
        return (
            self.db.query(self.model)
            .filter(self.model.question_id == question_id)
            .all()
        )
    
    def delete_by_question_id(self, question_id: str) -> None:
        """Delete question options by question_id.
        Args:
            question_id (str): The question_id to filter by.
        Returns:
            None
        """
        (
            self.db.query(self.model)
            .filter(self.model.question_id == question_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()