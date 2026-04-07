from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Response, status
from sqlalchemy.orm import Session

from app.api.models.user import User
from app.api.services.event import EventService
from app.api.v1.event import schemas
from app.core.dependencies.security import get_current_user
from app.db.database import get_db


event = APIRouter(prefix="/events", tags=["Events"])


@event.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.EventsListResponseModel,
    summary="Get all events",
    description="This endpoint retrieves events with pagination and filters",
)
def get_all_events(
    db: Annotated[Session, Depends(get_db)],
    page: int = 1,
    page_size: int = 10,
    title: Optional[str] = None,
    location_type: Optional[str] = None,
    past: Optional[bool] = None,
):
    """Endpoint to retrieve events with pagination and filters.

    Args:
        db (Annotated[Session, Depends]): Database session
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of items per page. Defaults to 10.
        title (Optional[str], optional): Filter by event title.
        location_type (Optional[str], optional): Filter by location type.
        past (Optional[bool], optional): Filter past events when true.
    """

    service = EventService(db=db)

    paginated_data = service.list_events(
        page=page,
        page_size=page_size,
        title=title,
        location_type=location_type,
        past=past,
    )

    paginated_data.items = [
        schemas.EventResponseData(**event.to_dict()) for event in paginated_data.items
    ]

    return schemas.EventsListResponseModel(
        status_code=status.HTTP_200_OK,
        message="Events retrieved successfully",
        data=paginated_data,
    )


@event.get(
    path="/{event_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.EventResponseModel,
    summary="Get an event by ID",
    description="This endpoint retrieves an event by its ID",
)
def get_event_by_id(
    event_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    """Endpoint to retrieve an event by its ID.

    Args:
        event_id (str): ID of the event to retrieve
        db (Annotated[Session, Depends]): Database session
    """

    service = EventService(db=db)

    event_model = service.get_event(event_id=event_id)

    response_data = schemas.EventResponseData(**event_model.to_dict())

    return schemas.EventResponseModel(
        status_code=status.HTTP_200_OK,
        message="Event retrieved successfully",
        data=response_data,
    )


@event.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.EventResponseModel,
    summary="Create a new event",
    description="This endpoint creates a new event",
)
async def create_event(
    schema: Annotated[schemas.EventForm, Form()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to create a new event.

    Args:
        schema (schemas.EventForm): Event creation schema
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated user
    """

    service = EventService(db=db)

    event_model = await service.create_event(schema=schema)

    response_data = schemas.EventResponseData(**event_model.to_dict())

    return schemas.EventResponseModel(
        status_code=status.HTTP_201_CREATED,
        message="Event created successfully",
        data=response_data,
    )


@event.put(
    path="/{event_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.EventResponseModel,
    summary="Update an existing event",
    description="This endpoint updates an existing event",
)
async def update_event(
    event_id: str,
    schema: Annotated[schemas.EventUpdateForm, Form()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to update an existing event.

    Args:
        event_id (str): ID of the event to update
        schema (schemas.EventUpdateForm): Event update schema
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated user
    """

    service = EventService(db=db)

    event_model = await service.update_event(event_id=event_id, schema=schema)

    response_data = schemas.EventResponseData(**event_model.to_dict())

    return schemas.EventResponseModel(
        status_code=status.HTTP_200_OK,
        message="Event updated successfully",
        data=response_data,
    )


@event.delete(
    path="/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an existing event",
    description="This endpoint deletes an existing event",
)
async def delete_event(
    event_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to delete an existing event.

    Args:
        event_id (str): ID of the event to delete
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated user
    """

    service = EventService(db=db)

    await service.delete_event(event_id=event_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)