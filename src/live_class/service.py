from datetime import datetime

from prisma.models import LiveClass
from src.utils import get_current_time
from src.live_class.model import LiveClassModel
from src.live_class.serializers import (
    CreateLiveClass,
    EditLiveClass,
)


class LiveClassService:
    def __init__(self) -> None:
        self.model = LiveClassModel()

    async def create(self, live_class: CreateLiveClass):
        new_live_class: LiveClass = await self.model.create(live_class)
        return new_live_class

    async def get(self, live_class_id: int):
        live_class: LiveClass = await self.model.get(live_class_id)
        return live_class

    async def get_by_batch(
            self,
            batch_id: int,
            _from: datetime = None,
            _to: datetime = None,
            skip: int = 0,
            limit: int = 10
    ):
        where = {
            "batch_id": batch_id
        }

        include = {
            "teacher": False,
            "batch": True
        }

        if _from:
            _to = _to if _to else get_current_time()
            where["class_starts_at"] = {"gte": _from, "lte": _to}

        return await self.model.find_many(where=where, include=include, skip=skip, limit=limit)

    async def update_live_class(
            self, live_class_id: int, edit_live_class_req: EditLiveClass
    ):
        live_class: LiveClass = await self.get(live_class_id)
        updated_live_class: LiveClass = await self.model.update(
            live_class_id, live_class, edit_live_class_req
        )
        return updated_live_class
