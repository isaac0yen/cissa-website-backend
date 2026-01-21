from sqlalchemy.orm import Session

from app.core.base.repository import BaseRepository
from app.api.models.test_attempt import TestAttempt, AttemptQuestion


class TestAttemptRepository(BaseRepository[TestAttempt]):
    """
    TestAttempt repository class for CRUD operations on TestAttempt model.
    This class inherits from BaseRepository and provides specific methods for TestAttempt model.
    Attributes:
        model (Type[TestAttempt]): The SQLAlchemy TestAttempt model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(TestAttempt, db)

class AttemptQuestionRepository(BaseRepository):
    """
    AttemptQuestion repository class for CRUD operations on AttemptQuestion model.
    This class inherits from BaseRepository and provides specific methods for AttemptQuestion model.
    Attributes:
        model (Type[AttemptQuestion]): The SQLAlchemy AttemptQuestion model class.
        db (Session): The SQLAlchemy session.
    """

    def __init__(self, db: Session):
        super().__init__(AttemptQuestion, db)

    # lock questions to an attempt by creating a new AttemptQuestion record
    # given a list of selected questions, associate them with the attempt
    # make sure to maintain the order of the questions
    def lock_questions_to_attempt(
        self, attempt_id: str, question_ids: list[str]
    ) -> list[AttemptQuestion]:
        """Lock questions to an attempt by creating AttemptQuestion records.
        Args:
            attempt_id (str): The ID of the test attempt.
            question_ids (list[str]): List of question IDs to lock to the attempt.
        Returns:
            list[AttemptQuestion]: List of created AttemptQuestion objects.
        """
        attempt_questions = []
        for order, question_id in enumerate(question_ids):
            attempt_question = AttemptQuestion(
                attempt_id=attempt_id,
                question_id=question_id,
                question_order=order,
            )
            attempt_questions.append(attempt_question)

        self.db.add_all(attempt_questions)
        self.db.commit()
        for aq in attempt_questions:
            self.db.refresh(aq)
        return attempt_questions