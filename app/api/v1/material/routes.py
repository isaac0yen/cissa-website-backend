from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from app.api.models.user import User
from app.api.services.material import MaterialService
from app.api.v1.material import schemas
from app.core.dependencies.security import get_current_user
from app.db.database import get_db
from app.utils.gdrive_helper import generate_download_link

material = APIRouter(prefix="/materials", tags=["Materials"])


@material.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MaterialsListResponseModel,
    summary="Get all materials",
    description="This endpoint retrieves materials with pagination and filters",
)
def get_all_materials(
    db: Annotated[Session, Depends(get_db)],
    page: int = 1,
    page_size: int = 10,
    title: Optional[str] = None,
    department: Optional[schemas.DepartmentType] = None,
    course_code: Optional[str] = None,
    level: Optional[schemas.LevelType] = None,
    semester: Optional[schemas.SemesterType] = None,
    material_type: Optional[schemas.MaterialFormatType] = None,
    session: Optional[str] = None,
):
    """Endpoint to retrieve materials with pagination and filters.

    Args:
        db (Annotated[Session, Depends]): Database session
        page (int, optional): Page number for pagination. Defaults to 1.
        page_size (int, optional): Number of items per page. Defaults to 10.
        title (Optional[str], optional): Filter by material title.
        department (Optional[schemas.DepartmentType], optional): Filter by department.
        course_code (Optional[str], optional): Filter by course code.
        level (Optional[schemas.LevelType], optional): Filter by material level.
        semester (Optional[schemas.SemesterType], optional): Filter by semester.
        material_type (Optional[schemas.MaterialFormatType], optional): Filter by material type.
        session (Optional[str], optional): Filter by session.
    """

    service = MaterialService(db=db)

    paginated_data = service.list(
        page=page,
        page_size=page_size,
        title=title,
        department=department,
        course_code=course_code,
        level=level,
        semester=semester,
        material_type=material_type,
        session=session,
    )

    paginated_data.items = [
        schemas.MaterialResponseData(**material.to_dict())
        for material in paginated_data.items
    ]

    return schemas.MaterialsListResponseModel(
        status_code=status.HTTP_200_OK,
        message="Materials retrieved successfully",
        data=paginated_data,
    )


@material.get(
    path="/{material_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MaterialResponseModel,
    summary="Get a material by ID",
    description="This endpoint retrieves a material by its ID",
)
def get_material_by_id(
    material_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    service = MaterialService(db=db)

    material = service.get(material_id)

    return schemas.MaterialResponseModel(
        status_code=status.HTTP_200_OK,
        message="Material retrieved successfully",
        data=schemas.MaterialResponseData(**material.to_dict()),
    )


@material.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MaterialResponseModel,
    summary="Create a new material",
    description="This endpoint creates a new material",
)
def create_material(
    schema: schemas.MaterialRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    service = MaterialService(db=db)

    schema.drive_url = generate_download_link(schema.drive_url)

    material = service.create(schema)

    return schemas.MaterialResponseModel(
        status_code=status.HTTP_201_CREATED,
        message="Material created successfully",
        data=schemas.MaterialResponseData(**material.to_dict()),
    )


@material.put(
    path="/{material_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.MaterialResponseModel,
    summary="Update an existing material",
    description="This endpoint updates an existing material",
)
def update_material(
    material_id: str,
    schema: schemas.MaterialUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    service = MaterialService(db=db)

    if schema.drive_url:
        schema.drive_url = generate_download_link(schema.drive_url)
    
    updated_material = service.update(material_id, schema)

    return schemas.MaterialResponseModel(
        status_code=status.HTTP_200_OK,
        message="Material updated successfully",
        data=schemas.MaterialResponseData(**updated_material.to_dict()),
    )


@material.delete(
    path="/{material_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a material",
    description="This endpoint deletes a material",
)
def delete_material(
    material_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
):
    """Endpoint to delete a material.

    Args:
        material_id (str): ID of the material to delete
        db (Annotated[Session, Depends]): Database session
        current_user (Annotated[User, Depends]): Current authenticated user
    """

    service = MaterialService(db=db)

    service.delete(material_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
