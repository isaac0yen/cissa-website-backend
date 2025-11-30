from fastapi import APIRouter, Depends, status, Response, Query
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from app.db.database import get_db
from app.core.dependencies.security import get_current_admin

from app.api.v1.tests import schemas
from app.api.services.test import TestService
from app.api.models.user import User

test_router = APIRouter(prefix="/tests", tags=["Test Management"])


@test_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.TestResponseModel,
    summary="Create a new test",
    description="This endpoint creates a new test (unpublished by default)",
)
def create_test(
    schema: schemas.TestCreateSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to create a new test

    Args:
        schema (schemas.TestCreateSchema): Test creation schema
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated admin user
    """

    service = TestService(db=db)

    test = service.create(schema=schema)

    response_data = schemas.TestBaseData(**test.to_dict())

    return schemas.TestResponseModel(
        status_code=status.HTTP_201_CREATED,
        message="Test created successfully",
        data=response_data,
    )


@test_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TestsListResponseModel,
    summary="Get all tests",
    description="This endpoint retrieves all tests with optional filters and pagination",
)
def get_all_tests(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    is_published: Optional[bool] = None,
    course_title: Optional[str] = None,
    course_code: Optional[str] = None,
):
    """Endpoint to retrieve all tests with filters

    Args:
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated admin user
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of items per page. Defaults to 10.
        is_published (Optional[bool], optional): Filter by publication status.
        course_title (Optional[str], optional): Search by course title.
        course_code (Optional[str], optional): Search by course code.
    """

    service = TestService(db=db)

    paginated_data = service.list_tests(
        page=page,
        page_size=page_size,
        is_published=is_published,
        course_title=course_title,
        course_code=course_code,
    )

    test_items = [
        schemas.TestBaseData(**test.to_dict())
        for test in paginated_data.items
    ]

    paginated_response = schemas.TestsPaginatedData(
        total_items=paginated_data.total_items,
        total_pages=paginated_data.total_pages,
        current_page=paginated_data.current_page,
        page_size=paginated_data.page_size,
        items=test_items,
    )

    return schemas.TestsListResponseModel(
        status_code=status.HTTP_200_OK,
        message="Tests retrieved successfully",
        data=paginated_response,
    )


@test_router.get(
    path="/{test_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TestResponseModel,
    summary="Get a test by ID",
    description="This endpoint retrieves a test by its ID",
)
def get_test_by_id(
    test_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to retrieve a test by its ID

    Args:
        test_id (str): ID of the test to retrieve
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated admin user
    """

    service = TestService(db=db)

    test = service.get_by_id(test_id=test_id)

    response_data = schemas.TestBaseData(**test.to_dict())

    return schemas.TestResponseModel(
        status_code=status.HTTP_200_OK,
        message="Test retrieved successfully",
        data=response_data,
    )


@test_router.put(
    path="/{test_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TestResponseModel,
    summary="Update an existing test",
    description="This endpoint updates an existing test",
)
def update_test(
    test_id: str,
    schema: schemas.TestUpdateSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to update an existing test

    Args:
        test_id (str): ID of the test to update
        schema (schemas.TestUpdateSchema): Test update schema
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated admin user
    """

    service = TestService(db=db)

    test = service.update(test_id=test_id, schema=schema)

    response_data = schemas.TestBaseData(**test.to_dict())

    return schemas.TestResponseModel(
        status_code=status.HTTP_200_OK,
        message="Test updated successfully",
        data=response_data,
    )


@test_router.patch(
    path="/{test_id}/publish",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TestResponseModel,
    summary="Publish a test",
    description="This endpoint publishes a test after validating it has sufficient questions",
)
def publish_test(
    test_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to publish a test

    Args:
        test_id (str): ID of the test to publish
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated admin user
    """

    service = TestService(db=db)

    test = service.publish(test_id=test_id)

    response_data = schemas.TestBaseData(**test.to_dict())

    return schemas.TestResponseModel(
        status_code=status.HTTP_200_OK,
        message="Test published successfully",
        data=response_data,
    )


@test_router.patch(
    path="/{test_id}/unpublish",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TestResponseModel,
    summary="Unpublish a test",
    description="This endpoint unpublishes a test",
)
def unpublish_test(
    test_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to unpublish a test

    Args:
        test_id (str): ID of the test to unpublish
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated admin user
    """

    service = TestService(db=db)

    test = service.unpublish(test_id=test_id)

    response_data = schemas.TestBaseData(**test.to_dict())

    return schemas.TestResponseModel(
        status_code=status.HTTP_200_OK,
        message="Test unpublished successfully",
        data=response_data,
    )


@test_router.delete(
    path="/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an existing test",
    description="This endpoint deletes an existing test and all associated questions",
)
def delete_test(
    test_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
):
    """Endpoint to delete an existing test

    Args:
        test_id (str): ID of the test to delete
        db (Annotated[Session, Depends): Database session
        current_user (Annotated[User, Depends): Current authenticated admin user
    """

    service = TestService(db=db)

    service.delete(test_id=test_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)