from datetime import date, datetime, time
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, StringConstraints

from app.core.base.schema import BaseResponseModel, PaginatedResponse

LevelType = Literal["100", "200", "300", "400"]
SemesterType = Literal["harmattan", "rain"]
DepartmentType = Literal["csc", "ift", "lis", "tcs", "mac"]

class MaterialRequest(BaseModel):
    title: str
    description: str
    course_code: str
    course_title: str
    level: LevelType
    semester: SemesterType
    material_type: str
    drive_url: str
    session: str
    departments: list[DepartmentType]

class MaterialUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    course_code: Optional[str] = None
    course_title: Optional[str] = None
    level: Optional[LevelType] = None
    semester: Optional[SemesterType] = None
    material_type: Optional[str] = None
    drive_url: Optional[str] = None
    session: Optional[str] = None
    departments: Optional[list[DepartmentType]] = None

class MaterialResponseData(BaseModel):
    id: str
    title: str
    description: Optional[str]
    course_code: str
    course_title: str
    level: LevelType
    semester: SemesterType
    material_type: str
    drive_url: str
    session: Optional[str]
    departments: list[DepartmentType]
    created_at: datetime
    updated_at: datetime

class MaterialResponseModel(BaseResponseModel):
    data: MaterialResponseData

class MaterialPaginatedResponse(PaginatedResponse):
    items: list[MaterialResponseData]

class MaterialsListResponseModel(BaseResponseModel):
    data: MaterialPaginatedResponse | PaginatedResponse