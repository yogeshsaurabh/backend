from typing import Optional

from pydantic import BaseModel


class Response(BaseModel):
    options: list[int] = []


class CreateQuizResponseReq(BaseModel):
    question_id: int
    response: Response


class CreateQuizResponse(BaseModel):
    student_id: int
    question_id: int
    response: Response


class EditQuizResponse(BaseModel):
    response: Optional[Response]
