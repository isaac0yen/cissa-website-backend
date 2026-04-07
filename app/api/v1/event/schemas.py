from datetime import date, datetime, time
from typing import Annotated, Literal, Optional

from fastapi import UploadFile
from pydantic import BaseModel, StringConstraints

from app.core.base.schema import BaseResponseModel, PaginatedResponseModel


class EventForm(BaseModel):
    title: Annotated[str, StringConstraints(max_length=255)]
    image: UploadFile
    description: str
    location: Annotated[str, StringConstraints(max_length=255)]
    location_type: Literal["physical", "online"]
    start_date: date
    end_date: Optional[date] = None
    start_time: time
    end_time: Optional[time] = None
    requires_ticket: bool = False
    ticket_url: Optional[Annotated[str, StringConstraints(max_length=2048)]] = None
    session: Annotated[str, StringConstraints(max_length=100)]


class EventUpdateForm(BaseModel):
    title: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    image: Optional[UploadFile] = None
    description: Optional[str] = None
    location: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    location_type: Optional[Literal["physical", "online"]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    requires_ticket: Optional[bool] = None
    ticket_url: Optional[Annotated[str, StringConstraints(max_length=2048)]] = None
    session: Optional[Annotated[str, StringConstraints(max_length=100)]] = None


class EventResponseData(BaseModel):
    id: str
    title: str
    description: str
    image_url: Optional[str]
    location: str
    location_type: str
    start_date: date
    end_date: Optional[date]
    start_time: time
    end_time: Optional[time]
    requires_ticket: bool
    ticket_url: Optional[str]
    session: str
    created_at: datetime


class EventResponseModel(BaseResponseModel):
    data: EventResponseData


class EventsListResponseModel(PaginatedResponseModel):
    pass