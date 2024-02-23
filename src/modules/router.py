from fastapi import APIRouter, Depends
from prisma.models import Module as ModuleModel

from src.auth.utils import get_current_admin, get_current_user
from src.modules.serializers import CreateModule
from src.modules.service import ModuleService

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post("/create")
async def create_new_module(create_req: CreateModule, _: dict = Depends(get_current_admin)):
    return await ModuleService().create_module(create_req)


@router.get("/{module_id}")
async def get_module_details(module_id: int, _: dict = Depends(get_current_user)):
    module_service = ModuleService()
    module: ModuleModel = await module_service.get_module(module_id)
    return module
