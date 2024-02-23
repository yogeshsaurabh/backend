from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateLiveClass(BaseModel):
    name: str
    module_id: int
    batch_id: int
    meeting_link: Optional[str]
    teacher_id: Optional[int]
    class_starts_at: datetime
    class_ends_at: datetime


class EditLiveClass(BaseModel):
    name: Optional[str]
    module_id: Optional[int]
    meeting_link: Optional[str]
    teacher_id: Optional[int]
    class_starts_at: Optional[datetime]
    class_ends_at: Optional[datetime]
