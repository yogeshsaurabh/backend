from prisma.models import Module

from src.modules.model import ModuleModel
from src.modules.serializers import CreateModule, EditModule


class ModuleService:
    def __init__(self) -> None:
        self.model = ModuleModel()

    async def create_module(self, module_data: CreateModule):
        module_data.description = module_data.description.json(exclude_unset=True)
        new_module: Module = await self.model.create(module_data)
        return new_module

    async def get_module(self, module_id: int) -> Module:
        module: Module = await self.model.get(id_=module_id)
        return module

    async def update_module(self, module_id: int, module_edit: EditModule):
        module: Module = await self.get_module(module_id)
        updated_module = await self.model.update(module_id, module, module_edit)
        return updated_module
