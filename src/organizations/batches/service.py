from prisma.models import Batch, Student

from src.organizations.batches.model import BatchModel
from src.organizations.batches.exceptions import BATCH_OUTSIDE_ORGANIZATION
from src.organizations.batches.serializers import (
    CreateBatch,
    EditBatch,
)
from src.students.model import StudentModel


class BatchService:
    def __init__(self) -> None:
        self.model = BatchModel()

    async def create(self, batch: CreateBatch):
        new_batch: Batch = await self.model.create(batch)
        return new_batch

    async def get(self, batch_id: int):
        batch: Batch = await self.model.get(batch_id)
        return batch

    async def update_batch(
            self, batch_id: int, edit_batch_req: EditBatch
    ):
        batch: Batch = await self.get(batch_id)
        updated_batch: Batch = await self.model.update(
            batch_id, batch, edit_batch_req
        )
        return updated_batch

    async def add_student_to_batch(
            self, student_id: int, batch_id: int
    ):
        student: Student = await StudentModel().get(student_id)
        batch: Batch = await self.get(batch_id)
        if student.organization_id != batch.organization_id:
            raise BATCH_OUTSIDE_ORGANIZATION

        # TODO: implement RAW query to check max member condition.

        return await StudentModel().join_batch(batch_id=batch.id, student_id=student_id)
