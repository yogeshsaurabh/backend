from typing import Optional

from pydantic import BaseModel


class CreateBatch(BaseModel):
    name: str
    available_seats: int
    organization_id: int


class EditBatch(BaseModel):
    name: Optional[str]
    available_seats: Optional[int]


class AddStudentToBatchReq(BaseModel):
    student_id: int
    batch_id: int


class RemoveStudentFromBatchReq(BaseModel):
    student_id: int
