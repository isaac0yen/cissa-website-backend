from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.models.test import Question, QuestionOption
from app.api.repositories.question import QuestionRepository, QuestionOptionRepository
from app.api.v1.questions import schemas
from app.core.base.schema import PaginatedResponse
from app.utils.logger import logger


class QuestionService:
    """
    Question service class for handling question-related operations.
    This class provides methods for creating, retrieving, updating,
    and deleting questions.
    """

    def __init__(self, db: Session):
        self.repository = QuestionRepository(db)
        self.option_repository = QuestionOptionRepository(db)

    def __validate_options(
        self, question: Question, options: List[schemas.QuestionOptionBaseData]
    ) -> List[schemas.QuestionOptionBaseData]:
        """
        Validates that
        - only one option is marked as correct.
        - there are at least two options provided.

        Args:
            options (List[schemas.QuestionOptionBaseData]): List of question options.
        Raises:
            HTTPException: If validation fails.
        Returns:
            List[schemas.QuestionOptionBaseData]: Validated list of question options.
        """

        # if something is wrong specify which question

        if len(options) < 2:
            logger.error(
                f"Validation error: Less than two options provided for question ID {question.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"At least two options are required for the question '{question.question_text[:30]}'.",
            )

        correct_count = sum(1 for option in options if option.is_correct)
        if correct_count != 1:
            logger.error(
                f"Validation error: {correct_count} correct options provided for question ID {question.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Exactly one option must be marked as correct for the question '{question.question_text[:30]}'.",
            )

        return options

    def create(
        self, test_id: str, schema: schemas.QuestionCreateSchema
    ) -> tuple[Question, List[QuestionOption]]:
        """
        Creates a new question with options after validating them.

        Args:
            test_id (str): The ID of the test to which the question belongs.
            schema (schemas.QuestionCreateSchema): Question creation schema.

        Returns:
            Question: The created question object.
            List[QuestionOption]: List of created question options.
        """

        question = Question(test_id=test_id, question_text=schema.question_text)
        validated_options = self.__validate_options(question, schema.options)

        try:
            logger.info(f"Creating question: {question.question_text[:50]}...")

            # Add question to session but don't commit yet
            self.repository.db.add(question)
            self.repository.db.flush()  # Get the ID without committing

            # Create options
            option_list = [
                QuestionOption(
                    question_id=question.id,
                    option_text=option.option_text,
                    is_correct=option.is_correct,
                )
                for option in validated_options
            ]

            logger.info(
                f"Creating {len(option_list)} options for question ID: {question.id}"
            )

            # Add options to session
            self.repository.db.add_all(option_list)

            # Commit everything atomically
            self.repository.db.commit()
            self.repository.db.refresh(question)

            logger.info(
                f"Successfully created question ID: {question.id} with {len(option_list)} options"
            )
            return question, option_list

        except HTTPException:
            # Re-raise validation errors
            self.repository.db.rollback()
            raise
        except Exception as e:
            # Rollback on any error
            self.repository.db.rollback()
            logger.error(
                f"Error creating question '{question.question_text[:50]}...': {str(e)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the question and options",
            )

    def get_by_id(self, question_id: str) -> Question:
        """
        Retrieves a question by its ID.

        Args:
            question_id (str): The ID of the question to retrieve.

        Returns:
            Question: The retrieved question object.
        """

        question = self.repository.get(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )
        return question

    def update(
        self, question_id: str, schema: schemas.QuestionUpdateSchema
    ) -> Question:
        """
        Updates an existing question.

        Args:
            question_id (str): The ID of the question to update.
            schema (schemas.QuestionUpdateSchema): Question update schema.

        Returns:
            Question: The updated question object.
        """

        question = self.repository.get(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )

        if question.test.is_published:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify questions in a published test",
            )

        try:
            # Update question text if provided
            if schema.question_text is not None:
                question.question_text = schema.question_text

            # Update options if provided
            if schema.options is not None:
                validated_options = self.__validate_options(question, schema.options)

                # Delete existing options and create new ones in same transaction
                logger.info(f"Updating options for question ID: {question.id}")

                # Delete existing options
                self.option_repository.delete_by_question_id(question.id)

                # Create new options
                option_list = [
                    QuestionOption(
                        question_id=question.id,
                        option_text=option.option_text,
                        is_correct=option.is_correct,
                    )
                    for option in validated_options
                ]

                # Add new options to session
                self.repository.db.add_all(option_list)

                logger.info(
                    f"Created {len(option_list)} new options for question ID: {question.id}"
                )

            # Update and commit the question
            logger.info(f"Updating question ID: {question.id}")
            updated_question = self.repository.update(question)

            return updated_question

        except HTTPException:
            # Re-raise validation  and business logic errors
            self.repository.db.rollback()
            raise
        except Exception as e:
            # Rollback on any error
            self.repository.db.rollback()
            logger.error(f"Error updating question ID {question.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the question",
            )

    def delete(self, question_id: str) -> bool:
        """
        Deletes a question by its ID.

        Args:
            question_id (str): The ID of the question to delete.

        Returns:
            bool: True if deletion was successful.
        """

        question = self.repository.get(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )

        if question.test.is_published:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete questions in a published test",
            )

        try:
            logger.info(f"Deleting question ID: {question.id}")
            return self.repository.delete(question_id)
        except Exception as e:
            logger.error(f"Error deleting question ID {question.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while deleting the question",
            )

    def bulk_create(
        self, test_id: str, schemas_list: List[schemas.QuestionCreateSchema]
    ) -> List[tuple[Question, List[QuestionOption]]]:
        """
        Creates multiple questions in bulk with ALL-OR-NOTHING transaction.
        If any question or option fails validation or creation, the entire operation is rolled back.

        Args:
            test_id (str): The ID of the test to which the questions belong.
            schemas_list (List[schemas.QuestionCreateSchema]): List of question creation schemas.
        Returns:
            List[tuple[Question, List[QuestionOption]]]: List of tuples containing created questions and their options.
        """

        if not schemas_list:
            return []

        try:
            # PHASE 1: Validate ALL questions and options BEFORE creating anything
            logger.info(
                f"Validating {len(schemas_list)} questions before bulk creation..."
            )
            questions_with_options: List[
                tuple[Question, List[schemas.QuestionOptionBaseData]]
            ] = []

            for index, schema in enumerate(schemas_list):
                try:
                    question = Question(
                        test_id=test_id, question_text=schema.question_text
                    )
                    validated_options = self.__validate_options(
                        question, schema.options
                    )
                    questions_with_options.append((question, validated_options))
                except HTTPException as e:
                    # Add question index to error message for better debugging
                    logger.error(
                        f"Validation failed for question at index {index}: {e.detail}"
                    )
                    raise HTTPException(
                        status_code=e.status_code,
                        detail=f"Question #{index + 1}: {e.detail}",
                    )

            logger.info("All %d questions validated successfully", len(schemas_list))

            # PHASE 2: Create ALL questions and options in a SINGLE TRANSACTION
            logger.info(
                f"Starting bulk creation of {len(questions_with_options)} questions..."
            )

            # Add all questions to session (not committed yet)
            questions = [q for q, _ in questions_with_options]
            self.repository.db.add_all(questions)
            self.repository.db.flush()  # Get IDs without committing

            logger.info("Questions added to session, creating options...")

            # Build all options with the question IDs
            all_options: List[QuestionOption] = []
            for i, question in enumerate(questions):
                _, validated_options = questions_with_options[i]
                for option in validated_options:
                    all_options.append(
                        QuestionOption(
                            question_id=question.id,
                            option_text=option.option_text,
                            is_correct=option.is_correct,
                        )
                    )

            # Add all options to session
            self.repository.db.add_all(all_options)

            # COMMIT everything atomically - all or nothing!
            self.repository.db.commit()

            logger.info(
                "Successfully bulk created %d questions with %d total options",
                len(questions),
                len(all_options),
            )

            # Refresh questions to get relationships
            for question in questions:
                self.repository.db.refresh(question)

            # PHASE 3: Group options by question for return value
            result: List[tuple[Question, List[QuestionOption]]] = []
            options_by_question = {}
            for option in all_options:
                if option.question_id not in options_by_question:
                    options_by_question[option.question_id] = []
                options_by_question[option.question_id].append(option)

            for question in questions:
                result.append((question, options_by_question.get(question.id, [])))

            return result

        except HTTPException:
            # Rollback and re-raise validation/business logic errors
            self.repository.db.rollback()
            raise
        except Exception as e:
            # Rollback on any unexpected error
            self.repository.db.rollback()
            logger.error("Error in bulk create operation: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during bulk creation: {str(e)}",
            )

    def list_questions(
        self,
        test_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse:
        """
        Retrieves a paginated list of questions with optional filters.

        Args:
            page (int): Page number.
            page_size (int): Number of items per page.
            test_id (Optional[str]): Filter by test ID.

        Returns:
            PaginatedResponse: Paginated response containing question items.
        """

        query = self.repository.db.query(Question)

        query = self.repository.filter_by_test_id(query, test_id)

        return self.repository.paginate(query, page, page_size)
