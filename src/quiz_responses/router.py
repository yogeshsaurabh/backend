from fastapi import APIRouter, Depends
from prisma.models import QuizResponse as QuizResponseModel

from src.auth.utils import get_current_admin, get_current_user
from src.quiz_responses.serializers import CreateQuizResponse, CreateQuizResponseReq
from src.quiz_responses.service import QuizResponseService

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
async def create_new_response(
    create_req: CreateQuizResponseReq,
    current_user: dict = Depends(
        get_current_user,
    ),
):
    student_id: int = current_user["id"]

    newResponseData = CreateQuizResponse(
        student_id=student_id,
        question_id=create_req.question_id,
        response=create_req.response,
    )
    return await QuizResponseService().create_response(newResponseData)


@router.get("/{response_id}")
async def get_response(response_id: int, _: dict = Depends(get_current_admin)):
    response_service = QuizResponseService()
    response: QuizResponseModel = await response_service.get_response(response_id)
    return response
