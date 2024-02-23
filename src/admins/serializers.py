from typing import Optional

from pydantic import BaseModel, SecretStr

from src.auth.serializers import UserRoles


class CreateAdminReq(BaseModel):
    username: str
    password: SecretStr


class CreateAdmin(BaseModel):
    username: str
    password: SecretStr

    class Config:
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }


class EditAdmin(BaseModel):
    username: Optional[str]


class TokenPayload(BaseModel):
    id: int
    exp: int
    role: UserRoles
