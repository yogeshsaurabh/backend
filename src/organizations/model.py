from prisma.models import Organization

from src.crud_base import CRUDBaseModel
from src.organizations.serializers import CreateOrganization, EditOrganization


class OrganizationModel(CRUDBaseModel[CreateOrganization, EditOrganization]):
    def __init__(self):
        super().__init__(Organization)

    async def get_by_name(self, name: str):
        return await super().get_unique(where={"name": name}, include={})
