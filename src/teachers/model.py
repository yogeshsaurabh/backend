from prisma.models import Teacher

from src.teachers.serializers import CreateTeacher, EditTeacher
from src.crud_base import CRUDBaseModel


class TeacherModel(CRUDBaseModel[CreateTeacher, EditTeacher]):
    def __init__(self):
        super().__init__(Teacher)
