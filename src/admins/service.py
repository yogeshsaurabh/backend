from prisma.models import Admin

from src.admins.model import AdminModel
from src.admins.serializers import CreateAdmin, CreateAdminReq, EditAdmin


def delete_password(admin: Admin):
    if hasattr(admin, "password"):
        del admin.password
    return admin


class AdminService:
    def __init__(self) -> None:
        self.model = AdminModel()

    async def create_admin(self, admin_req: CreateAdminReq):
        # create an instance of the admin database model
        admin_data = CreateAdmin(
            username=admin_req.username, password=admin_req.password
        )

        new_admin: Admin = await self.model.create(admin_data)
        return new_admin

    async def get_admin(self, admin_id: int) -> Admin:
        admin: Admin = await self.model.get(id_=admin_id)
        admin = delete_password(admin)
        return admin

    async def get_admin_by_username(self, username: str) -> Admin:
        admin: Admin = await self.model.get_by_username(username)
        admin = delete_password(admin)
        return admin

    async def update_admin(self, username: str, admin_edit: EditAdmin):
        admin = await self.get_admin_by_username(username)
        updated_admin = await self.model.update(admin.id, admin, admin_edit)
        delete_password(updated_admin)
        return updated_admin
