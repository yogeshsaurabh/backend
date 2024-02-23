from prisma.models import Batch

from src.crud_base import CRUDBaseModel
from src.organizations.batches.serializers import CreateBatch, EditBatch


class BatchModel(CRUDBaseModel[CreateBatch, EditBatch]):
    def __init__(self):
        super().__init__(Batch)
