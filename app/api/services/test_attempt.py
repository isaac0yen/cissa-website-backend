from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.api.models.test_attempt import TestAttempt
from app.api.repositories.question import QuestionRepository, QuestionOptionRepository
from app.api.repositories.test import TestRepository
from app.api.repositories.registration import RegistrationRepository
from app.api.repositories.student_profile import StudentProfileRepository
from app.api.repositories.test_attempt import (
    TestAttemptRepository,
    AttemptQuestionRepository,
)

from app.api.v1.attempts.schemas import (
    AttemptQuestionData,
    AttemptOptionData,
    FullAttemptData,
)
from app.utils.logger import logger


class TestAttemptService:
    """
    TestAttempt service class for handling business logic related to TestAttempts.
    """

    def __init__(self, db: Session):
        self.repository = TestAttemptRepository(db)
        self.attempt_question_repository = AttemptQuestionRepository(db)
        self.question_repository = QuestionRepository(db)
        self.question_option_repository = QuestionOptionRepository(db)
        self.test_repository = TestRepository(db)
        self.registration_repository = RegistrationRepository(db)
        self.student_profile_repository = StudentProfileRepository(db)

    def create_test_attempt(self, registration_id: str) -> FullAttemptData:
        """
        Create a new TestAttempt for a given registration ID, and populate it with associated AttemptQuestions.

        Args:
            registration_id (str): The registration ID for which to create the TestAttempt.

        Returns:
            FullAttemptData: The created TestAttempt along with its associated questions and options.
        """
        # step 1 - validation

        # registration id is used to get test and student info

        # Validate registration existence to show that the student is registered for the test
        registration = self.registration_repository.get(registration_id)
        if not registration:
            logger.error(f"Registration with ID {registration_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found."
            )

        # Validate student profile existence
        student_profile = self.student_profile_repository.get(registration.student_id)
        if not student_profile:
            logger.error(
                f"Student profile for user ID {registration.user_id} not found."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found.",
            )

        # Validate test existence
        test = self.test_repository.get(registration.test_id)
        if not test:
            logger.error(f"Test with ID {registration.test_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Test not found."
            )

        # step 2 - create test attempt
        test_attempt = TestAttempt(
            test_id=test.id,
            student_id=student_profile.id,
            score=0,
            max_score=int(test.questions_per_attempt),
            status="in_progress",
            started_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=test.duration),
            completed_at=None,
        )

        created_attempt = self.repository.create(test_attempt)

        # step 4 - generate attempt questions
        # fetch random questions for the test
        questions = self.question_repository.get_random_questions_by_test_id(
            test_id=test.id, limit=test.questions_per_attempt
        )

        # step 5 - lock questions to attempt
        questions_ids = [question.id for question in questions]
        _ = self.attempt_question_repository.lock_questions_to_attempt(
            attempt_id=created_attempt.id, question_ids=questions_ids
        )

        # step 6 - return response schema
        # attempt metadata + questions and options

        # first build a list of questions with options
        attempt_questions_data = []

        for question in questions:
            options = self.question_option_repository.get_by_question_id(question.id)
            option_data = [
                AttemptOptionData(id=option.id, option_text=option.option_text)
                for option in options
            ]
            question_data = AttemptQuestionData(
                id=question.id,
                question_text=question.question_text,
                options=option_data,
            )
            attempt_questions_data.append(question_data)

        return FullAttemptData(
            id=created_attempt.id,
            test_id=created_attempt.test_id,
            student_id=created_attempt.student_id,
            score=created_attempt.score,
            max_score=created_attempt.max_score,
            status=created_attempt.status,
            started_at=created_attempt.started_at,
            expires_at=created_attempt.expires_at,
            completed_at=created_attempt.completed_at,
            questions=attempt_questions_data,
        )
