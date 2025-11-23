from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.database import get_db
from app.core.dependencies.security import get_current_student
from app.api.models.user import User
from app.api.v1.student_profile import schemas
from app.api.services.student_profile import StudentProfileService


student_profile = APIRouter(prefix="/student/profile", tags=["Student Profile"])


@student_profile.get(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=schemas.StudentProfileResponse,
    summary="Get student profile",
    description="Get the profile of the currently logged-in student",
)
def get_my_profile(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_student)],
):
    """Get student profile for current user

    Args:
        db: Database session
        current_user: Current authenticated student user

    Returns:
        StudentProfileResponse: Profile data
    """
    service = StudentProfileService(db)
    profile = service.get_profile_by_user_id(current_user.id)

    profile_data = schemas.StudentProfileData(
        id=profile.id,
        user_id=profile.user_id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        created_at=str(profile.created_at),
        updated_at=str(profile.updated_at),
    )

    return schemas.StudentProfileResponse(
        status_code=status.HTTP_200_OK,
        message="Profile retrieved successfully",
        data=profile_data,
    )


@student_profile.put(
    path="",
    status_code=status.HTTP_200_OK,
    response_model=schemas.StudentProfileResponse,
    summary="Update student profile",
    description="Update the profile of the currently logged-in student",
)
def update_my_profile(
    schema: schemas.UpdateStudentProfileRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_student)],
):
    """Update student profile for current user

    Args:
        schema: Update request data
        db: Database session
        current_user: Current authenticated student user

    Returns:
        StudentProfileResponse: Updated profile data
    """
    service = StudentProfileService(db)
    profile = service.update_profile(current_user.id, schema)

    profile_data = schemas.StudentProfileData(
        id=profile.id,
        user_id=profile.user_id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        created_at=str(profile.created_at),
        updated_at=str(profile.updated_at),
    )

    return schemas.StudentProfileResponse(
        status_code=status.HTTP_200_OK,
        message="Profile updated successfully",
        data=profile_data,
    )
