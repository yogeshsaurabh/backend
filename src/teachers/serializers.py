from typing import Optional

from pydantic import BaseModel, SecretStr


class CreateTeacherReq(BaseModel):
    name: str
    password: SecretStr
    email: str
    phone_number: str
    age: Optional[int]


class CreateTeacher(BaseModel):
    name: str
    password: SecretStr
    email: str
    age: Optional[int]
    phone_number: Optional[str]

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}


class EditTeacher(BaseModel):
    name: Optional[str]
    age: Optional[int]
    phone_number: Optional[str]

    class Config:
        json_encoders = {SecretStr: lambda v: v.get_secret_value() if v else None}
