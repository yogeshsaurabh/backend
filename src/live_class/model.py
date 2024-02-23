from prisma.models import LiveClass

from src.crud_base import CRUDBaseModel
from src.live_class.serializers import CreateLiveClass, EditLiveClass


class LiveClassModel(CRUDBaseModel[CreateLiveClass, EditLiveClass]):
    def __init__(self):
        super().__init__(LiveClass)
