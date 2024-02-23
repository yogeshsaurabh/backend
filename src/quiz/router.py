from fastapi import APIRouter, Depends
from prisma.models import Question as QuestionModel

from src.auth.utils import get_current_admin, get_current_user
from src.quiz.serializers import CreateQuestion
from src.quiz.service import QuestionService

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/question/create")
async def create_new_question(
    create_req: CreateQuestion, _: dict = Depends(get_current_admin)
):
    return await QuestionService().create_question(create_req)


@router.get("/{question_id}")
async def get_question(question_id: int, _: dict = Depends(get_current_admin)):
    question_service = QuestionService()
    question: QuestionModel = await question_service.get_question(question_id)
    return question


@router.get("/")
async def get_quiz_by_grade(
    grade: int,
    skip: int = 0,
    limit: int = 60,
    _: dict = Depends(get_current_user),
):
    question_service = QuestionService()
    questions: list[QuestionModel] = await question_service.get_questions_by_grade(
        grade,
        skip,
        limit,
    )
    return {"quiz": questions}
