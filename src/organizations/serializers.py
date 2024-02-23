from typing import Optional

from pydantic import BaseModel, SecretStr


class CreateOrganization(BaseModel):
    name: str
    max_capacity: int


class EditOrganization(BaseModel):
    name: Optional[str]
    max_capacity: Optional[int]


class JoinOrganizationReq(BaseModel):
    activation_code: SecretStr


class AddStudentToOrganizationReq(JoinOrganizationReq):
    """Admin"""
    student_email: str
