from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import List

from app.core.base.schema import BaseResponseModel, PaginatedResponse


class TestDetailsData(BaseModel):
    """Test details for registration responses"""

    id: str
    course_code: str
    course_title: str
    duration: int
    questions_per_attempt: int
    price: Decimal


class RegistrationData(BaseModel):
    """Registration data model"""

    id: str
    student_id: str
    test_id: str
    created_at: datetime
    updated_at: datetime
    test: TestDetailsData


class RegistrationResponseModel(BaseResponseModel):
    """Single registration response"""

    data: RegistrationData


class RegistrationsPaginatedData(PaginatedResponse):
    """Paginated registrations response"""

    items: List[RegistrationData]


class RegistrationsListResponseModel(BaseResponseModel):
    """List of registrations response"""

    data: RegistrationsPaginatedData
