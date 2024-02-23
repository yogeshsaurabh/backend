from prisma.models import Admin

from src.admins.serializers import CreateAdmin, EditAdmin
from src.crud_base import CRUDBaseModel


class AdminModel(CRUDBaseModel[CreateAdmin, EditAdmin]):
    def __init__(self):
        super().__init__(Admin)

    async def get_by_username(self, username: str):
        return await super().get_unique(where={"username": username}, include={})
