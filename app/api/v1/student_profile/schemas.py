from typing import Annotated
from pydantic import BaseModel, StringConstraints
from app.core.base.schema import BaseResponseModel


class StudentProfileData(BaseModel):
    """Student profile data schema"""

    id: str
    user_id: str
    first_name: str
    last_name: str
    created_at: str
    updated_at: str


class UpdateStudentProfileRequest(BaseModel):
    """Request schema for updating student profile"""

    first_name: Annotated[str, StringConstraints(max_length=100)]
    last_name: Annotated[str, StringConstraints(max_length=100)]


class StudentProfileResponse(BaseResponseModel):
    """Response schema for student profile"""

    data: StudentProfileData
