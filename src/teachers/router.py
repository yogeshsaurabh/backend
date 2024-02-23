from fastapi import APIRouter, Depends
from prisma.models import Teacher as TeacherModel

from src.auth.basic_auth import BasicAuthHandler
from src.auth.serializers import UserRoles
from src.teachers.serializers import CreateTeacherReq
from src.teachers.service import TeacherService
from src.teachers.utils import get_current_teacher

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/register")
async def register_new_teacher(teacher_req: CreateTeacherReq):
    basic_auth_handler = BasicAuthHandler(TeacherModel, UserRoles.TEACHER)
    new_teacher = await basic_auth_handler.teacher_signup(teacher_req)
    return new_teacher


@router.get("/me")
async def get_teacher_details(teacher_token: dict = Depends(get_current_teacher)):
    teacher_id: int = teacher_token["id"]
    teacher_service = TeacherService()
    teacher: TeacherModel = await teacher_service.get_teacher(teacher_id)
    return teacher
