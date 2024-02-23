from enum import Enum
from typing import Optional

from pydantic import BaseModel, SecretStr


class UserRoles(Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class BasicAuthSignUp(BaseModel):
    username: str
    password: SecretStr

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}


class LoginReq(BaseModel):
    username: str
    password: SecretStr

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}


class EmailLoginReq(BaseModel):
    email: str
    password: SecretStr

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}


class Token(BaseModel):
    token: str


class TokenPayload(BaseModel):
    id: int
    exp: int
    role: UserRoles
    email: Optional[str]
    phone_number: Optional[str]
    organization_id: Optional[int]
