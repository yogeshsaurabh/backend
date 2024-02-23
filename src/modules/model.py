from prisma.models import Module

from src.modules.serializers import CreateModule, EditModule
from src.crud_base import CRUDBaseModel


class ModuleModel(CRUDBaseModel[CreateModule, EditModule]):
    def __init__(self):
        super().__init__(Module)
