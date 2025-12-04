from fastapi import APIRouter, Depends, status, Response, Query
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import get_db
from app.core.dependencies.security import get_current_student

from app.api.v1.registrations import schemas
from app.api.services.registration import RegistrationService
from app.api.models.user import User

registration_router = APIRouter(
    prefix="/tests/registrations", tags=["Student Test Registration"]
)


@registration_router.post(
    path="/{test_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.RegistrationResponseModel,
    summary="Register for a test",
    description="Register the current student for a published test (no payment required)",
)
def register_for_test(
    test_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_student)],
):
    """Register for a test

    Args:
        test_id (str): ID of the test to register for
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated student
    """

    service = RegistrationService(db=db)

    registration = service.create_registration(user_id=current_user.id, test_id=test_id)

    # Build response with test details
    test = registration.test
    test_details = schemas.TestDetailsData(
        id=test.id,
        course_code=test.course_code,
        course_title=test.course_title,
        duration=test.duration,
        questions_per_attempt=test.questions_per_attempt,
        price=test.price,
    )

    response_data = schemas.RegistrationData(
        id=registration.id,
        student_id=registration.student_id,
        test_id=registration.test_id,
        created_at=registration.created_at,
        updated_at=registration.updated_at,
        test=test_details,
    )

    return schemas.RegistrationResponseModel(
        status_code=status.HTTP_201_CREATED,
        message="Successfully registered for test",
        data=response_data,
    )


@registration_router.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=schemas.RegistrationsListResponseModel,
    summary="Get my test registrations",
    description="Retrieve all test registrations for the current student",
)
def get_my_registrations(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_student)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
):
    """Get my test registrations

    Args:
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated student
        page (int, optional): Page number. Defaults to 1.
        page_size (int, optional): Items per page. Defaults to 10.
    """

    service = RegistrationService(db=db)

    paginated_data = service.get_my_registrations(
        user_id=current_user.id, page=page, page_size=page_size
    )

    # Build response items with test details
    registration_items = []
    for registration in paginated_data.items:
        test = registration.test
        test_details = schemas.TestDetailsData(
            id=test.id,
            course_code=test.course_code,
            course_title=test.course_title,
            duration=test.duration,
            questions_per_attempt=test.questions_per_attempt,
            price=test.price,
        )

        registration_items.append(
            schemas.RegistrationData(
                id=registration.id,
                student_id=registration.student_id,
                test_id=registration.test_id,
                created_at=registration.created_at,
                updated_at=registration.updated_at,
                test=test_details,
            )
        )

    paginated_response = schemas.RegistrationsPaginatedData(
        total_items=paginated_data.total_items,
        total_pages=paginated_data.total_pages,
        current_page=paginated_data.current_page,
        page_size=paginated_data.page_size,
        items=registration_items,
    )

    return schemas.RegistrationsListResponseModel(
        status_code=status.HTTP_200_OK,
        message="Registrations retrieved successfully",
        data=paginated_response,
    )


@registration_router.get(
    path="/{registration_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.RegistrationResponseModel,
    summary="Get registration details",
    description="Get details of a specific registration (must be owned by current student)",
)
def get_registration_details(
    registration_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_student)],
):
    """Get registration details

    Args:
        registration_id (str): ID of the registration
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated student
    """

    service = RegistrationService(db=db)

    registration = service.get_registration_details(
        registration_id=registration_id, user_id=current_user.id
    )

    # Build response with test details
    test = registration.test
    test_details = schemas.TestDetailsData(
        id=test.id,
        course_code=test.course_code,
        course_title=test.course_title,
        duration=test.duration,
        questions_per_attempt=test.questions_per_attempt,
        price=test.price,
    )

    response_data = schemas.RegistrationData(
        id=registration.id,
        student_id=registration.student_id,
        test_id=registration.test_id,
        created_at=registration.created_at,
        updated_at=registration.updated_at,
        test=test_details,
    )

    return schemas.RegistrationResponseModel(
        status_code=status.HTTP_200_OK,
        message="Registration retrieved successfully",
        data=response_data,
    )


@registration_router.delete(
    path="/{registration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unregister from test",
    description="Delete a registration (unregister from test)",
)
def delete_registration(
    registration_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_student)],
):
    """Unregister from test

    Args:
        registration_id (str): ID of the registration to delete
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated student
    """

    service = RegistrationService(db=db)

    service.delete_registration(
        registration_id=registration_id, user_id=current_user.id
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
