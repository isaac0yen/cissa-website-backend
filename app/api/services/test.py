from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.api.models.test import Test
from app.api.repositories.test import TestRepository
from app.api.v1.tests import schemas
from app.core.base.schema import PaginatedResponse
from app.utils.logger import logger


class TestService:
    """
    Test service class for handling test-related operations.
    This class provides methods for creating, retrieving, updating,
    publishing, and deleting tests.
    """

    def __init__(self, db: Session):
        self.repository = TestRepository(db)

    def create(self, schema: schemas.TestCreateSchema) -> Test:
        """Creates a new test (unpublished by default)

        Args:
            schema: Test creation schema

        Returns:
            Test: Test object for the newly created test
        """
        test = Test(**schema.model_dump())
        test.is_published = False  # Always unpublished on creation

        try:
            logger.info(f"Creating test with course code: {test.course_code}")
            return self.repository.create(test)
        except Exception as e:
            logger.error(
                f"Error creating test with course code: {test.course_code} - {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the test",
            )

    def get_by_id(self, test_id: str) -> Test:
        """Retrieves a test by ID

        Args:
            test_id (str): ID of the test to retrieve

        Returns:
            Test: Test object
        """
        test = self.repository.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found",
            )
        return test

    def list_tests(
        self,
        page: int = 1,
        page_size: int = 10,
        is_published: Optional[bool] = None,
        course_title: Optional[str] = None,
        course_code: Optional[str] = None,
    ) -> PaginatedResponse:
        """Retrieves a paginated list of tests with optional filters

        Args:
            page (int): Page number (default: 1)
            page_size (int): Number of items per page (default: 10)
            is_published (Optional[bool]): Filter by publication status
            course_title (Optional[str]): Search by course title
            course_code (Optional[str]): Search by course code

        Returns:
            PaginatedResponse: Paginated response containing tests
        """
        query = self.repository.base_query()

        # Apply filters
        query = self.repository.filter_by_publication_status(query, is_published)
        query = self.repository.search_by_course_title(query, course_title)
        query = self.repository.search_by_course_code(query, course_code)

        # Sort by created_at descending (newest first)
        query = query.order_by(Test.created_at.desc())

        return self.repository.paginate(query, page, page_size)

    def update(self, test_id: str, schema: schemas.TestUpdateSchema) -> Test:
        """Updates an existing test

        Args:
            test_id (str): ID of the test to update
            schema: Test update schema

        Returns:
            Test: Updated test object
        """
        test = self.repository.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found",
            )

        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(test, key, value)

        try:
            logger.info(f"Updating test with ID: {test_id}")
            return self.repository.update(test)
        except Exception as e:
            logger.error(f"Error updating test with ID: {test_id} - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the test",
            )

    def publish(self, test_id: str) -> Test:
        """Publishes a test after validation

        Args:
            test_id (str): ID of the test to publish

        Returns:
            Test: Published test object

        Raises:
            HTTPException: If validation fails
        """
        test = self.repository.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found",
            )

        if test.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test is already published",
            )

        # Validate: Must have enough questions
        questions = test.questions  # Get questions via relationship
        question_count = len(questions)

        if question_count < test.questions_per_attempt:
            logger.error(
                f"Test {test_id} validation failed: "
                f"Has {question_count} questions but needs {test.questions_per_attempt}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Test must have at least {test.questions_per_attempt} questions. "
                    f"Currently has {question_count} question(s)."
                ),
            )

        # Validate each question has proper options
        validation_errors = []
        for idx, question in enumerate(questions, start=1):
            options = question.options  # Get options via relationship
            option_count = len(options)

            # Must have at least 2 options
            if option_count < 2:
                validation_errors.append(
                    f"Question #{idx} '{question.question_text[:50]}...' "
                    f"must have at least 2 options (has {option_count})"
                )
                continue

            # Must have exactly 1 correct answer
            correct_count = sum(1 for opt in options if opt.is_correct)
            if correct_count != 1:
                validation_errors.append(
                    f"Question #{idx} '{question.question_text[:50]}...' "
                    f"must have exactly 1 correct answer (has {correct_count})"
                )

        if validation_errors:
            logger.error(
                f"Test {test_id} validation failed with {len(validation_errors)} error(s)"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": f"Test validation failed: {len(validation_errors)} error(s) found",
                    "errors": validation_errors,
                },
            )

        logger.info(
            f"Test {test_id} validation passed: "
            f"{question_count} questions, all properly configured"
        )

        try:
            logger.info(f"Publishing test with ID: {test_id}")
            return self.repository.publish_test(test_id)
        except Exception as e:
            logger.error(f"Error publishing test with ID: {test_id} - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while publishing the test",
            )

    def unpublish(self, test_id: str) -> Test:
        """Unpublishes a test

        Args:
            test_id (str): ID of the test to unpublish

        Returns:
            Test: Unpublished test object
        """
        test = self.repository.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found",
            )

        if not test.is_published:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Test is already unpublished",
            )

        try:
            logger.info(f"Unpublishing test with ID: {test_id}")
            return self.repository.unpublish_test(test_id)
        except Exception as e:
            logger.error(f"Error unpublishing test with ID: {test_id} - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while unpublishing the test",
            )

    def delete(self, test_id: str) -> bool:
        """Deletes a test and all associated questions/options (cascade)

        Args:
            test_id (str): ID of the test to delete

        Returns:
            bool: True if deletion was successful
        """
        test = self.repository.get(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found",
            )

        try:
            logger.info(f"Deleting test with ID: {test_id}")
            return self.repository.delete(test_id)
        except Exception as e:
            logger.error(f"Error deleting test with ID: {test_id} - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the test",
            )
