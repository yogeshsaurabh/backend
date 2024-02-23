from datetime import datetime

from fastapi import APIRouter, Depends
from prisma.models import Student

from src.auth.utils import get_current_admin
from src.live_class.exceptions import BATCH_NOT_ALLOWED
from src.live_class.serializers import CreateLiveClass, EditLiveClass
from src.live_class.service import LiveClassService
from src.students.service import StudentService
from src.students.utils import get_current_student

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
async def create_new_live_class(create_req: CreateLiveClass, _: dict = Depends(get_current_admin)):
    return await LiveClassService().create(create_req)


@router.get("/")
async def get_live_class(
        batch_id: int,
        _from: datetime = None,
        _to: datetime = None,
        skip: int = 0,
        limit: int = 10,
        student_data: dict = Depends(get_current_student)
):
    student_id: int = student_data["id"]
    student: Student = await StudentService().get_student(student_id)

    if student.batch_id != batch_id:
        raise BATCH_NOT_ALLOWED

    return await LiveClassService().get_by_batch(batch_id, _from, _to, skip, limit)


@router.patch("/{live_class_id}")
async def edit_live_class(live_class_id: int, edit_req: EditLiveClass, _: dict = Depends(get_current_admin)):
    return await LiveClassService().update_live_class(live_class_id, edit_req)
