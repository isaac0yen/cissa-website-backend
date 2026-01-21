from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import get_db
from app.core.dependencies.security import get_current_student

from app.api.v1.attempts import schemas
from app.api.services.test_attempt import TestAttemptService
from app.api.models.user import User

attempt_router = APIRouter(prefix="/tests", tags=["Test Attempt Management"])


@attempt_router.get(
    path="/registrations/{registration_id}/attempts",
    status_code=status.HTTP_200_OK,
    response_model=schemas.AttemptResponseModel,
    summary="Create a new test attempt for a registration",
    description="This endpoint creates a new test attempt for a given registration ID and returns the attempt details with questions and options.",
)
def create_test_attempt(
    registration_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_student)],
):
    """Endpoint to create a new test attempt for a given registration ID.

    Args:
        registration_id (str): The registration ID for which to create the test attempt.
        db (Annotated[Session, Depends]): Database session.
        current_user (Annotated[User, Depends]): Current authenticated student user.
    """

    service = TestAttemptService(db=db)

    attempt = service.create_test_attempt(
        current_user=current_user, registration_id=registration_id
    )

    return schemas.AttemptResponseModel(
        status_code=status.HTTP_200_OK,
        message="Test attempt created successfully",
        data=attempt,
    )
