from fastapi import APIRouter, Depends
from prisma.models import Admin as AdminModel

from src.admins.serializers import CreateAdminReq
from src.admins.service import AdminService
from src.auth.basic_auth import BasicAuthHandler
from src.auth.serializers import UserRoles
from src.auth.utils import get_current_admin

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/register")
async def register_new_admin(admin_req: CreateAdminReq):
    basic_auth_handler = BasicAuthHandler(AdminModel, UserRoles.ADMIN)
    new_admin = await basic_auth_handler.admin_signup(admin_req)
    return new_admin


@router.get("/me")
async def get_admin_details(admin_token: dict = Depends(get_current_admin)):
    admin_id: int = admin_token["id"]
    admin_service = AdminService()
    admin: AdminModel = await admin_service.get_admin(admin_id)
    return admin
