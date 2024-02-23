from enum import Enum
from typing import Optional

from pydantic import BaseModel


class QuestionType(Enum):
    MCQ = "mcq"


class QuizOption(BaseModel):
    id: int
    text: str


class QuizQuestionData(BaseModel):
    question: str
    marks: int = 0
    type: QuestionType = QuestionType.MCQ
    options: list[QuizOption] = []


class CreateQuestion(BaseModel):
    grade: int
    question: QuizQuestionData
    answer_id: int


class EditQuestion(BaseModel):
    grade: Optional[int]
    question: Optional[QuizQuestionData]
    answer_id: Optional[int]
