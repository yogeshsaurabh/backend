from typing import Optional

from pydantic import BaseModel


class CreateActivationCode(BaseModel):
    organization_id: int
    activation_code: Optional[str]
    student_email: str


class EditActivationCode(BaseModel):
    activation_code: Optional[str]
    student_email: Optional[str]
