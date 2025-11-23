from typing import Annotated

from pydantic import BaseModel, StringConstraints, EmailStr
from app.core.base.schema import BaseResponseModel


class RegisterRequest(BaseModel):
    username: Annotated[str, StringConstraints(max_length=70)]
    email: Annotated[EmailStr, StringConstraints(max_length=254)]
    password: str
    first_name: Annotated[str, StringConstraints(max_length=100)]
    last_name: Annotated[str, StringConstraints(max_length=100)]


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, StringConstraints(max_length=254)]
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseResponseModel):
    access_token: str


class AuthResponseData(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str


class AuthResponse(BaseResponseModel):
    access_token: str
    refresh_token: str
    data: AuthResponseData


class UserResponse(BaseResponseModel):
    data: AuthResponseData
