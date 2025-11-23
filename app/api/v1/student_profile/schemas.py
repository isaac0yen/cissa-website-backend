from typing import Annotated, Optional
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

    first_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=100)]] = None


class StudentProfileResponse(BaseResponseModel):
    """Response schema for student profile"""

    data: StudentProfileData
