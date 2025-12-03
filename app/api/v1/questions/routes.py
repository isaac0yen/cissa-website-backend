from fastapi import APIRouter, Depends, status, Response, Query
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import get_db
from app.core.dependencies.security import get_current_admin

from app.api.v1.questions import schemas
from app.api.services.question import QuestionService
from app.api.models.user import User

question_router = APIRouter(prefix="/admin", tags=["Admin Question Management"])


@question_router.post(
    path="/tests/{test_id}/questions",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.QuestionResponseModel,
    summary="Add a question to a test",
    description="This endpoint adds a new question with options to a test",
)
def create_question(
    test_id: str,
    schema: schemas.QuestionCreateSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to add a question to a test

    Args:
        test_id (str): ID of the test to add the question to
        schema (schemas.QuestionCreateSchema): Question creation schema with options
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated admin user
    """

    service = QuestionService(db=db)

    question, options = service.create(test_id=test_id, schema=schema)

    # Build response with question and options
    question_dict = question.to_dict()
    option_list = [
        schemas.QuestionOptionBaseData(
            option_text=opt.option_text,
            is_correct=opt.is_correct,
        )
        for opt in options
    ]

    response_data = schemas.FullQuestionData(
        id=question_dict["id"],
        question_text=question_dict["question_text"],
        created_at=question_dict["created_at"],
        updated_at=question_dict["updated_at"],
        options=option_list,
    )

    return schemas.QuestionResponseModel(
        status_code=status.HTTP_201_CREATED,
        message="Question created successfully",
        data=response_data,
    )


@question_router.post(
    path="/tests/{test_id}/questions/bulk",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.QuestionsBulkCreateResponseModel,
    summary="Bulk upload questions to a test",
    description="This endpoint uploads multiple questions with options to a test in a single transaction (all-or-nothing)",
)
def bulk_create_questions(
    test_id: str,
    schema: schemas.QuestionsBulkCreateSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to bulk upload questions to a test

    Args:
        test_id (str): ID of the test to add questions to
        schema (schemas.QuestionsBulkCreateSchema): Bulk creation schema containing list of questions
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated admin user
    """

    service = QuestionService(db=db)

    questions_with_options = service.bulk_create(
        test_id=test_id, schemas_list=schema.questions
    )

    # Build response with all questions and options
    response_items = []
    for question, options in questions_with_options:
        question_dict = question.to_dict()
        option_list = [
            schemas.QuestionOptionBaseData(
                option_text=opt.option_text,
                is_correct=opt.is_correct,
            )
            for opt in options
        ]

        response_items.append(
            schemas.FullQuestionData(
                id=question_dict["id"],
                question_text=question_dict["question_text"],
                created_at=question_dict["created_at"],
                updated_at=question_dict["updated_at"],
                options=option_list,
            )
        )

    return schemas.QuestionsBulkCreateResponseModel(
        status_code=status.HTTP_201_CREATED,
        message=f"Successfully created {len(response_items)} question(s)",
        data=response_items,
    )


@question_router.get(
    path="/tests/{test_id}/questions",
    status_code=status.HTTP_200_OK,
    response_model=schemas.QuestionsListResponseModel,
    summary="Get all questions for a test",
    description="This endpoint retrieves all questions for a test with pagination",
)
def get_all_questions(
    test_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
):
    """Endpoint to retrieve all questions for a test

    Args:
        test_id (str): ID of the test to retrieve questions for
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated admin user
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of items per page. Defaults to 10.
    """

    service = QuestionService(db=db)

    paginated_data = service.list_questions(
        test_id=test_id,
        page=page,
        page_size=page_size,
    )

    # Build response with questions and their options
    question_items = []
    for question in paginated_data.items:
        question_dict = question.to_dict()
        option_list = [
            schemas.QuestionOptionBaseData(
                option_text=opt.option_text,
                is_correct=opt.is_correct,
            )
            for opt in question.options
        ]

        question_items.append(
            schemas.FullQuestionData(
                id=question_dict["id"],
                question_text=question_dict["question_text"],
                created_at=question_dict["created_at"],
                updated_at=question_dict["updated_at"],
                options=option_list,
            )
        )

    paginated_response = schemas.QuestionsPaginatedData(
        total_items=paginated_data.total_items,
        total_pages=paginated_data.total_pages,
        current_page=paginated_data.current_page,
        page_size=paginated_data.page_size,
        items=question_items,
    )

    return schemas.QuestionsListResponseModel(
        status_code=status.HTTP_200_OK,
        message="Questions retrieved successfully",
        data=paginated_response,
    )


@question_router.get(
    path="/questions/{question_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.QuestionResponseModel,
    summary="Get a question by ID",
    description="This endpoint retrieves a single question with its options by ID",
)
def get_question_by_id(
    question_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to retrieve a question by its ID

    Args:
        question_id (str): ID of the question to retrieve
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated admin user
    """

    service = QuestionService(db=db)

    question = service.get_by_id(question_id=question_id)

    # Build response with question and options
    question_dict = question.to_dict()
    option_list = [
        schemas.QuestionOptionBaseData(
            option_text=opt.option_text,
            is_correct=opt.is_correct,
        )
        for opt in question.options
    ]

    response_data = schemas.FullQuestionData(
        id=question_dict["id"],
        question_text=question_dict["question_text"],
        created_at=question_dict["created_at"],
        updated_at=question_dict["updated_at"],
        options=option_list,
    )

    return schemas.QuestionResponseModel(
        status_code=status.HTTP_200_OK,
        message="Question retrieved successfully",
        data=response_data,
    )


@question_router.put(
    path="/questions/{question_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.QuestionResponseModel,
    summary="Update a question",
    description="This endpoint updates an existing question and/or its options (only allowed for unpublished tests)",
)
def update_question(
    question_id: str,
    schema: schemas.QuestionUpdateSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to update an existing question

    Args:
        question_id (str): ID of the question to update
        schema (schemas.QuestionUpdateSchema): Question update schema (partial updates allowed)
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated admin user
    """

    service = QuestionService(db=db)

    question = service.update(question_id=question_id, schema=schema)

    # Build response with updated question and options
    question_dict = question.to_dict()
    option_list = [
        schemas.QuestionOptionBaseData(
            option_text=opt.option_text,
            is_correct=opt.is_correct,
        )
        for opt in question.options
    ]

    response_data = schemas.FullQuestionData(
        id=question_dict["id"],
        question_text=question_dict["question_text"],
        created_at=question_dict["created_at"],
        updated_at=question_dict["updated_at"],
        options=option_list,
    )

    return schemas.QuestionResponseModel(
        status_code=status.HTTP_200_OK,
        message="Question updated successfully",
        data=response_data,
    )


@question_router.delete(
    path="/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a question",
    description="This endpoint deletes a question and all its options (only allowed for unpublished tests)",
)
def delete_question(
    question_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to delete an existing question

    Args:
        question_id (str): ID of the question to delete
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated admin user
    """

    service = QuestionService(db=db)

    service.delete(question_id=question_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
