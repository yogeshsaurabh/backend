from prisma.models import Teacher

from src.teachers.model import TeacherModel
from src.teachers.serializers import CreateTeacher, EditTeacher, CreateTeacherReq


def delete_password(teacher: Teacher):
    if hasattr(teacher, "password"):
        del teacher.password
    return teacher


class TeacherService:
    def __init__(self) -> None:
        self.model = TeacherModel()

    async def create_teacher(self, teacher_req: CreateTeacherReq):
        # create an instance of the teacher database model
        teacher_data = CreateTeacher(**teacher_req.dict(exclude_unset=True))
        new_teacher: Teacher = await self.model.create(teacher_data)
        return new_teacher

    async def get_teacher(self, teacher_id: int) -> Teacher:
        teacher: Teacher = await self.model.get(id_=teacher_id)
        teacher = delete_password(teacher)
        return teacher

    async def update_teacher(self, teacher_id: int, teacher_edit: EditTeacher):
        teacher: Teacher = await self.get_teacher(teacher_id)
        updated_teacher = await self.model.update(teacher_id, teacher, teacher_edit)
        delete_password(updated_teacher)
        return updated_teacher
