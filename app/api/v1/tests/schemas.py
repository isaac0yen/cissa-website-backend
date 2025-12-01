from typing import Annotated, List, Optional
from datetime import datetime

from pydantic import BaseModel, StringConstraints
from app.core.base.schema import BaseResponseModel, PaginatedResponse

# test creation schema
class TestCreateSchema(BaseModel):
    course_code: Annotated[str, StringConstraints(max_length=10)]
    course_title: Annotated[str, StringConstraints(max_length=255)]
    duration: int
    questions_per_attempt: int
    price: float

# test update schema
class TestUpdateSchema(BaseModel):
    course_code: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    course_title: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    duration: Optional[int] = None
    questions_per_attempt: Optional[int] = None
    price: Optional[float] = None

# base test data
class TestBaseData(BaseModel):
    id: str
    course_code: str
    course_title: str
    duration: int
    questions_per_attempt: int
    price: float
    is_published: bool
    created_at: datetime
    updated_at: datetime

# test response schema
class TestResponseModel(BaseResponseModel):
    data: TestBaseData

# paginated test response schema
class TestsPaginatedData(PaginatedResponse):
    """Paginated response model with test items"""

    items: List[TestBaseData]

class TestsListResponseModel(BaseResponseModel):
    data: TestsPaginatedData